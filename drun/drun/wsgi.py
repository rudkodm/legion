#!/usr/bin/env python
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
Entry point for WSGI server
Example of usage: gunicorn drun.wsgi:application -k sync
"""

try:
    import docker_bootup
except ImportError:
    pass


from drun.pyserve import init_application
from drun.logging import redirect_to_stdout, set_log_level

set_log_level()
redirect_to_stdout()

application = init_application()