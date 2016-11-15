#!/bin/bash
source ports.sh
docker build --rm=true -t smtpcatcher .
docker run -e WEBSOCK=$WS_PORT -p $WEB_PORT:8025 -p $WS_PORT:8026 -p $SMTP_PORT:1025 -d start
