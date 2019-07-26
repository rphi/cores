FROM python:3.7
EXPOSE 8000

VOLUME ["/srv/static"]

RUN apt-get update \
    && apt-get install -y libldap2-dev libsasl2-dev libkrb5-dev \
    && apt-get clean

WORKDIR /srv/cores
ADD requirements.txt /srv/cores
RUN pip install -r requirements.txt
ADD . /srv/cores
ENTRYPOINT ["bash", "/srv/cores/start.sh"]
