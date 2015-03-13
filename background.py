from __future__ import absolute_import

from celery import Celery
from celery import Task
from kombu import Exchange, Queue
from datetime import timedelta
from celery.schedules import crontab

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
            'admin.order',
            Exchange('admin'),
            routing_key='admin.order',
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
        Queue(
            'admin.schedule',
            Exchange('admin'),
            routing_key='admin.schedule',
            delivery_mode=1,
            durable=False
        ),

    ),
    CELERY_IMPORTS=(
        "admin.tasks",
        "search.tasks",
    ),
    CELERYBEAT_SCHEDULE={
        'clean_slots': {
            'task': 'admin.scheduler.clean',
            'schedule': timedelta(minutes=5),
            'args': (),
            'options': {'queue': 'admin.schedule'},
        },
        'populate_slots': {
            'task': 'admin.scheduler.populate',
            'schedule': timedelta(minutes=1),
            'args': (),
            'options': {'queue': 'admin.schedule'},
        }
    }
)


class DBTask(Task):
    abstract = True
    _dbsession = None
    _redis = None

    @property
    def db(self):
        if not self._dbsession:
            self._dbsession = db.Session()
        return self._dbsession

    @property
    def r(self):
        self._redis = db.Redis()
        return self._redis

    def on_success(self, retval, task_id, args, kwargs):
        self.db.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.db.close()


if __name__ == "__main__":
    celery.start()