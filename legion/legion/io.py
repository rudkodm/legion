#
#    Copyright 2017 EPAM Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
"""
legion model export / load
"""

import datetime
import getpass
import json
import os
import zipfile

import dill
from pandas import DataFrame

import legion
import legion.config
import legion_core.model.types
from legion_core.model.types import deduct_types_on_pandas_df
from legion.utils import TemporaryFolder, get_git_revision, string_to_bool
from legion_core.model.model_id import get_model_id, is_model_id_auto_deduced


def _get_column_types(param_types):
    """
    Build dict with ColumnInformation from param_types argument for export function

    :param param_types: pandas DF with custom dict or pandas DF.
    Custom dict contains of column_name => legion_core.model.types.BaseType
    :type param_types tuple(:py:class:`pandas.DataFrame`, dict) or :py:class:`pandas.DataFrame`
    :return: dict[str, :py:class:`legion_core.model.types.ColumnInformation`] -- column name => column information
    """
    pandas_df_sample = None
    custom_props = None

    if isinstance(param_types, tuple) and len(param_types) == 2 \
            and isinstance(param_types[0], DataFrame) \
            and isinstance(param_types[1], dict):

        pandas_df_sample = param_types[0]
        custom_props = param_types[1]
    elif isinstance(param_types, DataFrame):
        pandas_df_sample = param_types
    else:
        raise Exception('Provided invalid param types: not tuple[DataFrame, dict] or DataFrame')

    return deduct_types_on_pandas_df(data_frame=pandas_df_sample, extra_columns=custom_props)


class ModelContainer:
    """
    Archive representation of model with meta information (properties, str => str)
    """

    ZIP_COMPRESSION = zipfile.ZIP_STORED
    ZIP_FILE_MODEL = 'model'
    ZIP_FILE_INFO = 'info.json'

    def __init__(self, file, is_write=False, do_not_load_model=False):
        """
        Create model container (archive) from existing (when is_write=False) or from empty (when is_write=True)

        :param file: path to file for load or save in future
        :type file: str
        :param is_write: flag for create empty container (not read)
        :type is_write: bool
        :param do_not_load_model: load only meta information
        :type do_not_load_model: bool
        """
        self._file = file
        self._is_saved = not is_write
        self._do_not_load_model = do_not_load_model
        self._model = None
        self._properties = {}

        if self._is_saved:
            self._load()

    def _load(self):
        """
        Load from file

        :return: None
        """
        if not os.path.exists(self._file):
            raise Exception('File not existed: %s' % (self._file,))

        try:
            with TemporaryFolder('legion-model-save') as temp_directory:
                with zipfile.ZipFile(self._file, 'r') as stream:
                    model_path = stream.extract(self.ZIP_FILE_MODEL,
                                                os.path.join(temp_directory.path, self.ZIP_FILE_MODEL))
                    info_path = stream.extract(self.ZIP_FILE_INFO,
                                               os.path.join(temp_directory.path, self.ZIP_FILE_INFO))

                if not self._do_not_load_model:
                    with open(model_path, 'rb') as file:
                        self._model = dill.load(file)

                with open(info_path, 'r') as file:
                    self._load_info(file)
        except zipfile.BadZipFile:
            raise Exception('Model files is not a zip file: %s (size: %dKb)' %
                            (self._file, os.path.getsize(self._file) / 1024))

    def _load_info(self, file):
        """
        Read properties from file-like object (using .read)

        :param file: source file
        :type file: file-like object
        :return: None
        """
        self._properties = json.load(file)

    def _write_info(self, file):
        """
        Write properties to file-like object (using .write)

        :param file: target file
        :type file: file-like object
        :return: None
        """
        json.dump(self._properties, file)

    def _add_default_properties(self):
        """
        Add default properties during saving of model

        :return: None
        """
        model_id = get_model_id()
        if not model_id or is_model_id_auto_deduced():
            raise Exception('Cannot get model_id. Please set using legion.init_model(<name>)')

        self['model.id'] = model_id
        self['model.class'] = self._model.__class__.__name__
        self['model.module'] = self._model.__class__.__module__
        self['model.version'] = self._model.version
        self['legion.version'] = legion_core.__version__

        self['jenkins.build_number'] = os.environ.get(*legion.config.BUILD_NUMBER)
        self['jenkins.build_id'] = os.environ.get(*legion.config.BUILD_ID)
        self['jenkins.build_tag'] = os.environ.get(*legion.config.BUILD_TAG)
        self['jenkins.build_url'] = os.environ.get(*legion.config.BUILD_URL)

        self['jenkins.git_commit'] = os.environ.get(*legion.config.GIT_COMMIT)
        self['jenkins.git_branch'] = os.environ.get(*legion.config.GIT_BRANCH)

        self['jenkins.node_name'] = os.environ.get(*legion.config.NODE_NAME)
        self['jenkins.job_name'] = os.environ.get(*legion.config.JOB_NAME)

    @property
    def model(self):
        """
        Get instance of model if it has been loaded or saved

        :return: :py:class:`legion.model.IMLModel` -- instance of model
        """
        if not self._is_saved:
            raise Exception('Cannot get model on non-saved container')

        return self._model

    def save(self, model_instance):
        """
        Save to file

        :param model_instance: model
        :type model_instance: :py:class:`legion.model.IMLModel`
        :return: None
        """
        self._model = model_instance
        self._add_default_properties()

        with TemporaryFolder('legion-model-save') as temp_directory:
            with open(os.path.join(temp_directory.path, self.ZIP_FILE_MODEL), 'wb') as file:
                dill.dump(model_instance, file, recurse=True)
            with open(os.path.join(temp_directory.path, self.ZIP_FILE_INFO), 'wt') as file:
                self._write_info(file)

            with zipfile.ZipFile(self._file, 'w', self.ZIP_COMPRESSION) as stream:
                stream.write(os.path.join(temp_directory.path, self.ZIP_FILE_MODEL), self.ZIP_FILE_MODEL)
                stream.write(os.path.join(temp_directory.path, self.ZIP_FILE_INFO), self.ZIP_FILE_INFO)

    def __enter__(self):
        """
        Return self on context enter

        :return: :py:class:`legion.io.ModelContainer`
        """
        return self

    def __exit__(self, exit_type, value, traceback):
        """
        Call remove on context exit

        :param exit_type: -
        :param value: -
        :param traceback: -
        :return: None
        """
        pass

    def __setitem__(self, key, item):
        """
        Set property value (without save)

        :param key: key
        :type key: str
        :param item: value
        :type key: str
        :return: None
        """
        self._properties[key] = item

    def __getitem__(self, key):
        """
        Get property value

        :param key: key
        :type key: str
        :return: str -- value
        """
        return self._properties[key]

    def __len__(self):
        """
        Get count of properties

        :return: int -- count of properties
        """
        return len(self._properties)

    def __delitem__(self, key):
        """
        Remove property by key

        :param key: key
        :type key: str
        :return: None
        """
        del self._properties[key]

    def has_key(self, k):
        """
        Check that property with specific key exists

        :param k: key
        :type k: str
        :return: bool -- check result
        """
        return k in self._properties

    def update(self, *args, **kwargs):
        """
        Update property dict with another values

        :param args: args
        :type args: tuple
        :param kwargs: kwargs
        :type args: dict
        :return: any result of update
        """
        return self._properties.update(*args, **kwargs)

    def keys(self):
        """
        Get tuple of properties keys

        :return: tuple of properties keys
        """
        return tuple(self._properties.keys())

    def values(self):
        """
        Get tuple of properties values

        :return: tuple of properties values
        """
        return tuple(self._properties.values())

    def items(self):
        """
        Get tuple of properties (key, value)

        :return: tuple of (key, value)
        """
        return self._properties.items()

    def get(self, key, default=None):
        """
        Get property value or default value

        :param key: key
        :type key: str
        :param default: any default value
        :type default: any
        :return: str or value of default
        """
        if key in self._properties:
            return self[key]
        return default

    def __contains__(self, k):
        """
        Check that property with specific key exists

        :param k: key
        :type k: str
        :return: bool check result
        """
        return k in self._properties

    def __iter__(self):
        """
        Iterate over properties

        :return: iterator
        """
        return iter(self._properties)


def deduce_param_types(data_frame, optional_dictionary=None):
    """
    Deduce param types of pandas DF. Optionally overwrite to custom legion.BaseType

    :param data_frame: pandas DF
    :type data_frame: :py:class:`pandas.DataFrame`
    :param optional_dictionary: custom dict contains of column_name => legion_core.model.types.BaseType
    :type optional_dictionary: dict[str, :py:class:`legion_core.model.types.BaseType`]
    :return: dict[str, :py:class:`legion.types.ColumnInformation`]
    """
    if optional_dictionary:
        return _get_column_types((data_frame, optional_dictionary))

    return _get_column_types(data_frame)


def deduce_model_file_name(version=None):
    """
    Get model file name

    :param version: version of model
    :type version: str or None
    :return: str -- auto deduced file name
    """
    if not version:
        version = '0.0'

    model_id = get_model_id()
    if not model_id or is_model_id_auto_deduced():
        raise Exception('Cannot get model_id. Please set using legion.init_model(<name>)')

    date_string = datetime.datetime.now().strftime('%y%m%d%H%M%S')

    valid_user_names = [os.getenv(env) for env in legion.config.MODEL_NAMING_UID_ENV if os.getenv(env)]
    user_id = valid_user_names[0] if valid_user_names else getpass.getuser()

    commit_id = get_git_revision(os.getcwd())
    if not commit_id:
        commit_id = '0000'

    file_name = '%s-%s+%s.%s.%s.model' % (model_id, str(version), date_string, user_id, commit_id)

    if string_to_bool(os.getenv(*legion.config.EXTERNAL_RESOURCE_USE_BY_DEFAULT)):
        return '///%s' % file_name

    default_prefix = os.getenv(*legion.config.LOCAL_DEFAULT_RESOURCE_PREFIX)
    if default_prefix:
        return os.path.join(default_prefix, file_name)

    return file_name
