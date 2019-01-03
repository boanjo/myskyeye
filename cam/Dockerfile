FROM tensorflow/tensorflow:1.12.0

MAINTAINER Anders Boan Johansson <epkboan@gmail.com>

RUN python --version
RUN apt-get update && yes | apt-get upgrade
RUN apt-get install -y git
#RUN apt-get install -y git python-pil python-lxml
RUN apt-get install -y libmysqlclient-dev

# Make sure you grab the latest version
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.3.0/protoc-3.3.0-linux-x86_64.zip

# Unzip
RUN unzip protoc-3.3.0-linux-x86_64.zip -d protoc3

# Move protoc to /usr/local/bin/
RUN mv protoc3/bin/* /usr/local/bin/

# Move protoc3/include to /usr/local/include/
RUN mv protoc3/include/* /usr/local/include/

RUN mkdir -p /tensorflow/models
RUN git clone https://github.com/tensorflow/models.git /tensorflow/models
WORKDIR /tensorflow/models/research
RUN protoc object_detection/protos/*.proto --python_out=.
ENV PYTHONPATH=/tensorflow/models/research:/tensorflow/models/research/slim

RUN pip install opencv-python-headless
RUN pip install opencv-contrib-python-headless

RUN pip install psutil
RUN pip install mysqlclient
RUN pip install imutils
RUN pip install http
RUN pip install requests

RUN mkdir /app
RUN mkdir /app/utils
RUN mkdir /app/model
RUN mkdir /app/output
RUN mkdir /app/log
WORKDIR /app
ADD *.py /app/

ADD model/* /app/model/
ADD utils/*.py /app/utils/
