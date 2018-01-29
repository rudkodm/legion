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
DRun env names
"""

BUILD_NUMBER = 'BUILD_NUMBER', 0
BUILD_ID = 'BUILD_ID', None
BUILD_URL = 'BUILD_URL', None
BUILD_TAG = 'BUILD_TAG', None

GIT_COMMIT = 'GIT_COMMIT', None
GIT_BRANCH = 'GIT_BRANCH', None

JOB_NAME = 'JOB_NAME', None
NODE_NAME = 'NODE_NAME', None

MODEL_SERVER_URL = 'MODEL_SERVER_URL', 'http://edge'
MODEL_ID = 'MODEL_ID', None
MODEL_FILE = 'MODEL_FILE', None

STATSD_HOST = 'STATSD_HOST', 'graphite'
STATSD_PORT = 'STATSD_PORT', 8125
STATSD_NAMESPACE = 'STATSD_NAMESPACE', 'legion.model'

CONSUL_ADDR = 'CONSUL_ADDR', 'consul'
CONSUL_PORT = 'CONSUL_PORT', 8500

LEGION_ADDR = 'LEGION_ADDR', '0.0.0.0'
LEGION_PORT = 'LEGION_PORT', 5000
IP_AUTODISCOVER = 'IP_AUTODISCOVER', 'true'

GRAPHITE_HOST = 'GRAPHITE_HOST', 'graphite'
GRAPHITE_PORT = 'GRAPHITE_PORT', 2003
GRAPHITE_NAMESPACE = 'GRAPHITE_NAMESPACE', 'stats.legion.model'

GRAFANA_URL = 'GRAFANA_URL', 'http://grafana:3000/'
GRAFANA_USER = 'GRAFANA_USER', 'admin'
GRAFANA_PASSWORD = 'GRAFANA_PASSWORD', 'admin'

EXTERNAL_RESOURCE_USE_BY_DEFAULT = 'EXTERNAL_RESOURCE_USE_BY_DEFAULT', 'true'
EXTERNAL_RESOURCE_PROTOCOL = 'EXTERNAL_RESOURCE_PROTOCOL', 'https'
EXTERNAL_RESOURCE_HOST = 'EXTERNAL_RESOURCE_HOST', 'localhost'
EXTERNAL_RESOURCE_USER = 'EXTERNAL_RESOURCE_USER', None
EXTERNAL_RESOURCE_PASSWORD = 'EXTERNAL_RESOURCE_PASSWORD', None

MODEL_NAMING_UID_ENV = 'JUPYTERHUB_USER', 'NB_USER', 'BUILD_ID'
DEBUG = 'DEBUG', 'false'
REGISTER_ON_CONSUL = 'REGISTER_ON_CONSUL', 'true'
REGISTER_ON_GRAFANA = 'REGISTER_ON_GRAFANA', 'true'
FLASK_APP_SETTINGS_FILES = 'FLASK_APP_SETTINGS_FILES', None
