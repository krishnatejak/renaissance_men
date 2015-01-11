from __future__ import absolute_import

from celery import Celery
from celery import Task
from kombu import Exchange, Queue

import config
import db


celery = Celery(
    'renaissance_celery',
    broker=config.CELERY_BROKER,
)

celery.conf.update(
    CELERY_IGNORE_RESULT=True,
    CELERY_ACCEPT_CONTENT=['pickle'],
    CELERY_CREATE_MISSING_QUEUES=False,
    CELERY_DEFAULT_QUEUE='default',
    CELERY_QUEUES=(
        Queue(
            'default',
            Exchange('default'),
            routing_key='default',
            delivery_mode=2,
            durable=True
        ),
        Queue(
            'admin.serviceprovider',
            Exchange('admin'),
            routing_key='admin.serviceprovider',
            delivery_mode=2,
            durable=True
        ),
        Queue(
            'admin.service',
            Exchange('admin'),
            routing_key='admin.service',
            delivery_mode=1,
            durable=False
        ),
        Queue(
            'admin.job',
            Exchange('admin'),
            routing_key='admin.job',
            delivery_mode=1,
            durable=False
        ),
        Queue(
            'admin.user',
            Exchange('admin'),
            routing_key='admin.user',
            delivery_mode=1,
            durable=False
        ),
        Queue(
            'search.getdistances',
            Exchange('admin'),
            routing_key='search.getdistances',
            delivery_mode=1,
            durable=False
        ),

    ),
    CELERY_IMPORTS=(
        "admin.tasks",
        "search.tasks",
    ),
)


class DBTask(Task):
    abstract = True
    _dbsession = None
    _redis = None

    @property
    def db(self):
        self._dbsession = db.Session()
        return self._dbsession

    @property
    def r(self):
        self._redis = db.Redis()
        return self._redis

    def on_success(self, retval, task_id, args, kwargs):
        if self.db:
            self.db.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.db:
            self.db.close()


if __name__ == "__main__":
    celery.start()