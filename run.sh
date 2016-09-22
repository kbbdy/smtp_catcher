#!/bin/bash
source ports.sh
docker build --rm=true -t smtpcatcher .
docker run --rm -it -e WEBSOCK=$WS_PORT -p $WEB_PORT:8025 -p $WS_PORT:8026 -p $SMTP_PORT:1025 smtpcatcher
