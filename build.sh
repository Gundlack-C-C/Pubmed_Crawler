
#!/bin/bash
IMAGE="pupymed/crawler"

# Enbable/Disable Docker Build
if [ $1 ] ; 
then 
	FORCE_UPDATE=true 
else 
	FORCE_UPDATE=false 
fi

#Create Directories if not existing
PATH_LOG="./.log"

mkdir -p $PATH_LOG

#Setup
echo "Building Image - ${IMAGE} - ForceUpdate:${FORCE_UPDATE}" | tee ${PATH_LOG}/build.log
if "$FORCE_UPDATE";
then
	echo "Build $IMAGE" | tee -a ${PATH_LOG}/build.log
	docker build --force-rm --no-cache -t ${IMAGE} . >> ${PATH_LOG}/build.log 2>&1
else
	echo "Build $IMAGE with cache" | tee -a ${PATH_LOG}/build.log
	docker build --force-rm -t ${IMAGE} . >> ${PATH_LOG}/build.log 2>&1
fi