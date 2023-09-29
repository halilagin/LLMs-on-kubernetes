FROM ubuntu:22.04

USER root
RUN apt-get update && \
apt-get install -y wget ca-certificates software-properties-common curl git python3.10 python3-pip
#RUN add-apt-repository  "deb http://apt.postgresql.org/pub/repos/apt/ lsb_release -cs-pgdg main"
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN add-apt-repository "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main"
#sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ lsb_release -cs-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'

RUN apt-get update
RUN apt-get -y install libpq-dev  postgresql-client 
RUN pip install --quiet python-dotenv pipenv
COPY Pipfile /
COPY Pipfile.lock /
RUN cd / && pipenv install --system --verbose 
