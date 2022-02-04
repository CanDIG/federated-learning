# syntax=docker/dockerfile:latest
# miniforge is necessary for ML library installations to succeed in Docker on M1 machines. It also will work fine with Intel and AMD machines.
FROM condaforge/miniforge3:latest
ADD . /code
WORKDIR /code

LABEL Maintainer="CanDIG Project"

USER root

RUN apt update

RUN conda install --file conda-requirements.txt \
    && pip install -r requirements.txt

ADD init.sh /
RUN chmod +x /init.sh

CMD ["/init.sh"]