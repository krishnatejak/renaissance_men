#!/bin/bash

VIRTUALENV_DIR=/home/ubuntu/renv
APP_DIR=/home/ubuntu/renaissance_men

cd ${VIRTUALENV_DIR}
source bin/activate

echo "starting tornado..."

cd ${APP_DIR}

exec python service.py