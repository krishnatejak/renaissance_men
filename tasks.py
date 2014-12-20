from __future__ import absolute_import

from celery import Celery
from kombu import Exchange, Queue

import config


celery = Celery(
    'renaissance_celery',
    broker=config.CELERY_BROKER,
)

celery.conf.update(
    CELERY_IGNORE_RESULT=True,
    CELERY_CREATE_MISSING_QUEUES=False,
    CELERY_QUEUES=(
        Queue(
            'admin.serviceprovider.add',
            Exchange('admin'),
            routing_key='admin.serviceprovider.add',
            delivery_mode=2,
            durable=True
        ),
        Queue(
            'admin.serviceprovider.otp',
            Exchange('admin'),
            routing_key='admin.serviceprovider.otp',
            delivery_mode=1,
            durable=False
        ),

    ),
    CELERY_IMPORTS=(
        "admin.tasks",
    ),
)

if __name__ == "__main__":
    celery.start()