#!/bin/bash

echo "##### Input ######"
printf "Container Environment: [%s]\n" "$MODE"
printf "Application name : [%s]\n" "$APPLICATION_NAME"
printf "Listen Port : [%s]\n" "$PORT"
printf "Log level : [%s]\n" "$LOG_LEVEL"
echo "##################"
echo ""

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
elif [ "$MODE" = "Worker" ]; then
    echo "Worker Mode"
	pthon3 app_workermq.py
elif [ "$MODE" = "Service" ]; then
    echo "Service Mode"
	python3 app_server.py
elif [ "$MODE" = "Dev" ]; then
    echo "Development Mode - Sleep to connect to container"
    /bin/sh -c "while sleep 1000; do :; done"
else
	echo "Unknown Argument [${MODE}]"
fi

echo "Success!"
