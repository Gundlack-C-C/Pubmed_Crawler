#!/bin/bash
[ -z "$1" ] && TARGETS="ccc ct" || TARGETS=${1}

mkdir -p ./log

#Rebuild image
echo "Rebuild image studycrawler"
docker build -t studycrawler . 2>&1 | tee ./log/build.log

for target in $TARGETS
do
	if [ $target = "ct" ];
	then
		echo "Run Crawler Clinical Trials.gov" | tee ./log/docker-run.log
		./docker-run-ct.sh 2>&1 | tee -a ./log/docker-run.log
	elif [ $target = "ccc" ];
	then
		echo "Run Crawler CCC" | tee -a ./log/docker-run.log
		./docker-run-ccc.sh 2>&1 | tee -a ./log/docker-run.log 
	else
		echo "Unkown target " $target
	fi
done
