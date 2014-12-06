from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgres import ARRAY

from models import Base


__all__ = ['Service', 'ServiceProvider']


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256), nullable=False)


class ServiceProvider(Base):
    __tablename__ = 'service_provider'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(512), nullable=False)
    skills = Column("skills", ARRAY(String), nullable=False)
    availability = Column("availability", Boolean, default=False)
    phone_number = Column("phone_number", String(20), nullable=False)
    address = Column("address", String(2048), nullable=False)
    home_location = Column("home_location", ARRAY(Float), nullable=False)
    office_location = Column("office_location", ARRAY(Float), nullable=False)
    cost_per_hour = Column("cost", Float, default=0.0)
    service = Column("service", ForeignKey('service.id'))

