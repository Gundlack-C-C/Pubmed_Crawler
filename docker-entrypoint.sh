#!/bin/bash

MODE=$1
DATA_DIR=$2

echo "docker-entrypoint.sh executing ..."

if [ "$MODE" = "ct" ]; then
	echo "[ct_gov] Start crawler for ClinicalTrials.gov"
	if [ $DATA_DIR ]; then
		echo "Crawling all files from ${DATA_DIR}"
		rm -rf ./out/data_$DATA_DIR.json
		scrapy crawl ct_gov -o ./out/data_$DATA_DIR.json -a part=$DATA_DIR
	else
		echo "Crawling all available files"
		rm -rf ./out/data_all.json
		scrapy crawl ct_gov -o ./out/data_all.json
	fi
elif [ "$MODE" == "ccc" ]; then
	echo "[ccc] Start crawler for Studienregister Erlangen"
	scrapy crawl ccc -o ./out/data_$DATA_DIR.json
else
	echo "Unknown Argument [${MODE}]"
fi

echo "Output in [./out/data_${DATA_DIR}.json]"
echo "Fertig!"
