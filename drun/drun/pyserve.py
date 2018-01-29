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
Flask app
"""

import os
import logging
import consul
from flask import Flask, Blueprint, request, jsonify, redirect
from flask import current_app as app

import drun.io
import drun.env
import drun.grafana
import drun.model as mlmodel
import drun.utils as utils

LOGGER = logging.getLogger(__name__)


class HttpProtocolHandler:
    def parse_request(self, input_request):
        """
        Produce a model input dictionary from HTTP request (GET/POST fields, and Files)

        :param input_request: request object
        :type input_request: :py:class:`Flask.request`
        :return: dict with requested fields
        """
        result = {}

        # Fill in URL parameters
        for k in input_request.args:
            result[k] = input_request.args[k]

        # Fill in POST parameters
        for k in input_request.form:
            result[k] = input_request.form[k]

        # Fill in Files:
        for k in input_request.files:
            result[k] = input_request.files[k].read()

        return result

    def prepare_response(self, response):
        """
        Produce an HTTP response from a model output

        :param response: a model output
        :type response: dict[str, any]
        :return: bytes
        """
        return jsonify(response)


protocol_handler = HttpProtocolHandler()

blueprint = Blueprint('pyserve', __name__)


@blueprint.route('/')
def root():
    """
    Return static file for root query

    :return: :py:class:`Flask.Response` -- response index file
    """
    return redirect('index.html')


# TODO: Add model check
@blueprint.route('/api/model/<model_id>/info')
def model_info(model_id):
    """
    Get model description

    :param model_id: model id
    :type model_id: str
    :return: :py:class:`Flask.Response` -- model description
    """
    # assert model_id == app.config['MODEL_ID']

    model = app.config['model']

    return jsonify(model.description)


# TODO: Add model check
@blueprint.route('/api/model/<model_id>/invoke', methods=['POST', 'GET'])
def model_invoke(model_id):
    """
    Call model for calculation

    :param model_id: model name
    :type model_id: str
    :return: :py:class:`Flask.Response` -- result of calculation
    """
    # TODO single configuration for Flask/CLI
    # assert model_id == app.config['MODEL_ID']

    input_dict = protocol_handler.parse_request(request)

    model = app.config['model']

    output = model.apply(input_dict)

    return protocol_handler.prepare_response(output)


@blueprint.route('/healthcheck')
def healthcheck():
    """
    Check that model is OK

    :return: str -- status string
    """
    return 'OK'


def init_model(application):
    """
    Load model from app configuration

    :param application: Flask app
    :type application: :py:class:`Flask.app`
    :return: model instance
    """
    if 'MODEL_FILE' in application.config:
        file = application.config['MODEL_FILE']
        LOGGER.info("Loading model from %s", file)
        with drun.io.ModelContainer(file) as container:
            model = container.model
    else:
        LOGGER.info("Instantiated dummy model")
        model = mlmodel.DummyModel()
    return model


def create_application():
    """
    Create Flask application and register blueprints

    :return: :py:class:`Flask.app` -- Flask application instance
    """
    application = Flask(__name__, static_url_path='')

    application.register_blueprint(blueprint)

    return application


def register_service(application):
    """
    Register application in Consul

    :param application: Flask application instance
    :type application: :py:class:`Flask.app`
    :return: None
    """
    consul_host = application.config['CONSUL_ADDR']
    consul_port = int(application.config['CONSUL_PORT'])
    client = consul.Consul(host=consul_host, port=consul_port)

    service = application.config['MODEL_ID']

    addr = application.config['LEGION_ADDR']
    port = int(application.config['LEGION_PORT'])

    print('Registering model %s located at %s:%d on http://%s:%s' % (service, addr, port, consul_host, consul_port))

    client.agent.service.register(
        service,
        address=addr,
        port=port,
        tags=['legion', 'model'],
        check=consul.Check.http('http://%s:%d/healthcheck' % (addr, port), '2s')
    )


def register_dashboard(application):
    """
    Register application in Grafana (create dashboard)

    :param application: Flask application instance
    :type application: :py:class:`Flask.app`
    :return: None
    """
    host = os.environ.get(*drun.env.GRAFANA_URL)
    user = os.environ.get(*drun.env.GRAFANA_USER)
    password = os.environ.get(*drun.env.GRAFANA_PASSWORD)

    print('Creating Grafana client for host: %s, user: %s, password: %s' % (host, user, '*' * len(password)))
    client = drun.grafana.GrafanaClient(host, user, password)
    client.create_dashboard_for_model(application.config['MODEL_ID'])


def apply_cli_args(application, args):
    """
    Set Flask app instance configuration from arguments

    :param application: Flask app instance
    :type application: :py:class:`Flask.app`
    :param args: arguments
    :type args: :py:class:`argparse.Namespace`
    :return: None
    """
    args_dict = vars(args)
    for k, v in args_dict.items():
        if v is not None:
            application.config[k.upper()] = v


def apply_env_argument(application, name, cast=None):
    """
    Update application config if ENV variable exists

    :param application: Flask app instance
    :type application: :py:class:`Flask.app`
    :param name: environment variable name
    :type name: str
    :param cast: casting of str variable
    :type cast: Callable[[str], Any]
    :return: None
    """
    if name in os.environ:
        value = os.getenv(name)
        if cast:
            value = cast(value)

        application.config[name] = value


def apply_env_args(application):
    """
    Set Flask app instance configuration from environment

    :param application: Flask app instance
    :type application: :py:class:`Flask.app`
    :return: None
    """
    apply_env_argument(application, drun.env.MODEL_ID[0])
    apply_env_argument(application, drun.env.MODEL_FILE[0])

    apply_env_argument(application, drun.env.CONSUL_ADDR[0])
    apply_env_argument(application, drun.env.CONSUL_PORT[0])

    apply_env_argument(application, drun.env.LEGION_ADDR[0])
    apply_env_argument(application, drun.env.LEGION_PORT[0])
    apply_env_argument(application, drun.env.IP_AUTODISCOVER[0], utils.string_to_bool)

    apply_env_argument(application, drun.env.DEBUG[0], utils.string_to_bool)
    apply_env_argument(application, drun.env.REGISTER_ON_CONSUL[0], utils.string_to_bool)


def init_application(args=None):
    """
    Initialize configured Flask application instance, register application on consul
    Overall configuration priority: config_default.py, env::FLASK_APP_SETTINGS_FILES file,
    ENV parameters, CLI parameters

    :param args: arguments if provided
    :type args: :py:class:`argparse.Namespace` or None
    :return: :py:class:`Flask.app` -- application instance
    """
    application = create_application()

    # 4th priority: config from file with defaults values
    application.config.from_pyfile('config_default.py')

    # 3rd priority: config from file (path to file from ENV)
    application.config.from_envvar(drun.env.FLASK_APP_SETTINGS_FILES[0], True)

    # 2nd priority: config from ENV variables
    apply_env_args(application)

    # 1st priority: config from CLI args
    if args:
        apply_cli_args(application, args)

    # Check LEGION_ADDR if IP_AUTODISCOVER enabled (by default)
    if application.config['IP_AUTODISCOVER']:
        cfg_addr = application.config['LEGION_ADDR']
        if cfg_addr == "" or cfg_addr == "0.0.0.0":
            application.config['LEGION_ADDR'] = utils.detect_ip()

    # Put a model object into application configuration
    application.config['model'] = init_model(application)

    # Register instance on Consul
    if application.config['REGISTER_ON_CONSUL']:
        register_service(application)
        logging.info('Consul consensus achieved')
    else:
        logging.info('Registration on Consul has been skipped due to configuration')

    # Register dashboard in Grafana
    # if application.config['REGISTER_ON_GRAFANA']:
    #     register_dashboard(application)
    #     logging.info('Grafana dashboard has been registered')
    # else:
    #     logging.info('Registration on Grafana has been skipped due to configuration')

    return application


def serve_model(args):
    """
    Serve model

    :param args: arguments
    :type args: :py:class:`argparse.Namespace`
    :return: None
    """
    logging.info('Legion pyserve initializing')
    application = init_application(args)

    application.run(host=application.config['LEGION_ADDR'],
                    port=application.config['LEGION_PORT'],
                    debug=application.config['DEBUG'],
                    use_reloader=False)

    return application
