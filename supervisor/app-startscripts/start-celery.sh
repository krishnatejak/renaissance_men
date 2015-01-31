#!/bin/bash

VIRTUALENV_DIR=/home/ubuntu/renv
APP_DIR=/home/ubuntu/renaissance_men
APP_NAME=background
cd ${VIRTUALENV_DIR}
source bin/activate

echo "starting tornado..."

cd ${APP_DIR}

exec celery worker --app=${APP_NAME} -c1 -l info