#
#    Copyright 2018 EPAM Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

FROM k8s.gcr.io/fluentd-elasticsearch:v2.0.4

RUN gem install fluent-plugin-s3 -v '~>1.0.0'


# Install legion dependencies
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    g++ apt-utils python3-dev python3-pip python3-setuptools file wget git \
    libtiff5-dev libjpeg62-turbo-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev \
    tcl8.6-dev tk8.6-dev python-tk python3-tk

RUN pip3 install "numpy>=1.11.2"

# Copy bootstrap script
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# Copy template
COPY fluentd.t /etc/fluent/fluentd.t

# Install additional required packages
RUN apt-get update && apt-get install -y procps

# Install legion
ARG pip_extra_index_params=""
ARG pip_legion_version_string=""

RUN pip3 install $pip_extra_index_params legion$pip_legion_version_string

CMD /run.sh $FLUENTD_ARGS