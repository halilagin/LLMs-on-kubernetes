#FROM ubuntu:22.04
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04
FROM nvcr.io/nvidia/pytorch:22.08-py3
ENV TZ=Europe/London \
    DEBIAN_FRONTEND=noninteractive


USER root
RUN apt-get update 
RUN apt-get install -y wget ca-certificates software-properties-common curl git python3.10 python3-pip 
#RUN add-apt-repository  "deb http://apt.postgresql.org/pub/repos/apt/ lsb_release -cs-pgdg main"
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
#RUN add-apt-repository ppa:deadsnakes/ppa 
RUN add-apt-repository "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main"
#sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ lsb_release -cs-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

RUN apt-get update && \
apt-get install -y libpq-dev  postgresql-client 
RUN pip install --quiet python-dotenv pipenv
WORKDIR /
COPY Pipfile /
#RUN pipenv --python /opt/conda/bin/python3 && \
#pipenv lock && pipenv --clear && pipenv --rm && \
#pipenv install --system --deploy
#COPY Pipfile.lock /
#RUN cd / && pipenv install --system --verbose 
