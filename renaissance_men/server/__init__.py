from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from renaissance_men.cmn_infra.config import get_sys_config

print 'came here'
#Creating the sqlalchemy engine and the Base.
engine = create_engine(get_sys_config('SQLALCHEMY_DATABASE_URI'), echo=False)


