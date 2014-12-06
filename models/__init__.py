from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import config

DB_URL = '{ENGINE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

DB_ENGINE = create_engine(
    DB_URL.format(**config.DATABASES['default']), echo=config.DEBUG
)

Base = declarative_base()

from service import *

Base.metadata.create_all(bind=DB_ENGINE)