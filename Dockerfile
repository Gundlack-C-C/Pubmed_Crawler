FROM python:3.7

WORKDIR /usr/src/app

#Install Dependency
COPY ./requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

COPY ./ /usr/src/app