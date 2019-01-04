FROM tensorflow/tensorflow:1.12.0

MAINTAINER Anders Boan Johansson <epkboan@gmail.com>

RUN apt-get update && yes | apt-get upgrade
RUN apt-get install -y git \
                       python-pil \
		       python-lxml \
		       tzdata \
		       libmysqlclient-dev

# Grab a good version of Google Protobuf Compiler
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.3.0/protoc-3.3.0-linux-x86_64.zip
RUN unzip protoc-3.3.0-linux-x86_64.zip -d protoc3
RUN mv protoc3/bin/* /usr/local/bin/
RUN mv protoc3/include/* /usr/local/include/

# Grab the object_detection research models and code
RUN mkdir -p /tensorflow/models
RUN git clone https://github.com/tensorflow/models.git /tensorflow/models
WORKDIR /tensorflow/models/research
RUN protoc object_detection/protos/*.proto --python_out=.
ENV PYTHONPATH=/tensorflow/models/research:/tensorflow/models/research/slim

RUN pip install opencv-python-headless \
                opencv-contrib-python-headless \
		mysqlclient \
		psutil \
		imutils \
		http \
		requests
		
RUN mkdir -p /app/utils
RUN mkdir -p /app/model
RUN mkdir -p /app/output
WORKDIR /app
ADD *.py /app/
ADD model/* /app/model/
ADD utils/*.py /app/utils/
