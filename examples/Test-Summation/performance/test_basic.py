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
import os

from legion.model.model_tests import LocustTaskSet
import legion.config

from locust import HttpLocust, task


class TaskSet(LocustTaskSet):
    @task()
    def invoke_nine_decode(self):
        self._invoke_model(a=10, b=20)

    def on_start(self):
        self.setup_model('test_summation')


class TestLocust(HttpLocust):
    task_set = TaskSet
    min_wait = 0
    max_wait = 0
