from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dictalchemy import DictableModel

import config


DB_URL = '{ENGINE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

DB_ENGINE = create_engine(
    DB_URL.format(**config.DATABASES['default']), echo=config.DEBUG
)

Base = declarative_base(bind=DB_ENGINE, cls=DictableModel)

Session = sessionmaker(bind=DB_ENGINE)