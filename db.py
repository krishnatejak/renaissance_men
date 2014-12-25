from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dictalchemy import DictableModel

import redis

import config


DB_URL = '{ENGINE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

DB_ENGINE = create_engine(
    DB_URL.format(**config.DATABASES['default']), echo=config.DEBUG
)

Base = declarative_base(bind=DB_ENGINE, cls=DictableModel)

Session = sessionmaker(bind=DB_ENGINE)

REDIS_CONN_POOL = redis.ConnectionPool(
    max_connections=200,
    **config.DATABASES['redis']
)

Redis = lambda: redis.Redis(connection_pool=REDIS_CONN_POOL)

# maintain single instance for redis
session_redis = redis.StrictRedis(**config.DATABASES['redis'])
