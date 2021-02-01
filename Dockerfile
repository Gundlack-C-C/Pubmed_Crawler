FROM python:3-onbuild
COPY ./app /usr/src/app

COPY ./docker-entrypoint.sh /usr/src/app/dockerInit/
ENTRYPOINT ["/usr/src/app/dockerInit/docker-entrypoint.sh"]