# syntax=docker/dockerfile:latest
FROM condaforge/miniforge3:latest
ADD . /code
WORKDIR /code

LABEL Maintainer="CanDIG Project"

USER root

RUN apt update

# TODO: remove unneeded dependencies
RUN conda install --file conda-requirements.txt \
    && pip install -r requirements.txt

ADD init.sh /
RUN chmod +x /init.sh

CMD ["/init.sh"]
