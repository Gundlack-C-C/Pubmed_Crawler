#!/bin/bash
IMAGE="pupymed/crawler"

QUERY_IN=$1

#Create Directories if not existing
PATH_LOG="./.log"
PATH_OUT="./.out"

mkdir -p $PATH_LOG
mkdir -p $PATH_OUT

#Run
echo "Starting Container with Image - ${IMAGE} ..." | tee -a ${PATH_LOG}/crawler.log
docker run --rm \
	--mount type=bind,src="$(pwd)"/.out,dst=/usr/src/app/.out \
	--mount type=bind,src="$(pwd)"/.log,dst=/usr/src/app/.log \
	${IMAGE} \
	python3 ./app_crawl_pubmed.py ${QUERY_IN} --production
echo "... Container Running" | tee -a ${PATH_LOG}/crawler.log