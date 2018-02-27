FROM python:2.7

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY . /opt/drenaj

WORKDIR /opt/drenaj

RUN pip install -r requirements.txt

RUN python ./configure.py ./host-configs/config-docker.yaml ./drenaj/drenaj_api/config/config.py

WORKDIR /opt/drenaj/drenaj

ENTRYPOINT python -m drenaj_api.appstartup

