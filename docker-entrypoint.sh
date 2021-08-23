#!/bin/bash

echo "##### Input ######"
printf "Container Environment: [%s]\n" "$MODE"
printf "Application name : [%s]\n" "$APPLICATION_NAME"
printf "Listen Port : [%s]\n" "$PORT"
printf "Log level : [%s]\n" "$LOG_LEVEL"
echo "##################"
echo ""

if [ "$MODE" = "Worker" ]; then
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
