# syntax=docker/dockerfile:latest

ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION}-slim
ADD . /src
WORKDIR /src

LABEL Maintainer="CanDIG Project"

USER root

RUN pip install -r requirements.txt -r experiment-requirements.txt

ADD entrypoint.sh /

CMD ["/entrypoint.sh"]