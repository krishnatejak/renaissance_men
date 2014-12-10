from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgres import ARRAY, JSON
from sqlalchemy.orm import relationship, backref

import db


__all__ = ['Service', 'ServiceProvider']


class Service(db.Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256), nullable=False)
    service_providers = relationship('ServiceProvider', backref=backref('service'))
    trash = Column("trash", Boolean, default=False)


class ServiceProvider(db.Base):
    __tablename__ = 'service_provider'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(512), nullable=False)
    availability = Column("availability", Boolean, default=False)
    phone_number = Column("phone_number", String(20))
    address = Column("address", String(2048))
    home_location = Column("home_location", ARRAY(Float, dimensions=1))
    office_location = Column("office_location", ARRAY(Float, dimensions=1))
    cost = Column("cost", Float, default=0.0)
    service_id = Column("service", ForeignKey('service.id'))
    experience = Column("experience", Float, default=0.0)
    skills = Column("skills", ARRAY(JSON, dimensions=1))
    trash = Column("trash", Boolean, default=False)

    class Meta(object):
        follow = ['service']
        exclude = ['id', 'trash']
        fk = ['service_id']

