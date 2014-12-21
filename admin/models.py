from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy import DateTime, Enum
from sqlalchemy.dialects.postgres import ARRAY, JSON
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from cryptacular.bcrypt import BCRYPTPasswordManager

import db


__all__ = ['Service', 'ServiceProvider', 'Job', 'ServiceSkill', 'User']


class Service(db.Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256), nullable=False)
    service_providers = relationship('ServiceProvider', backref=backref('service'))
    jobs = relationship('Job', backref=backref('service'))
    skills = relationship('ServiceSkill', backref=backref('service'))
    trash = Column("trash", Boolean, default=False)

    class Meta(object):
        follow = ['skills']
        follow_exclude = ['service_provider_id', 'trash', 'service_id', 'id', 'inspection']
        exclude = ['trash']
        fk = []


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
    skills = relationship('ServiceSkill', backref=backref('service_provider'))
    jobs = relationship('Job', backref=backref('service_provider'))
    verified = Column("verified", Boolean, default=False)
    gcm_reg_id = Column("gcm_reg_id", String)
    range = Column("service_range", Integer, default=5)
    trash = Column("trash", Boolean, default=False)

    class Meta(object):
        follow = ['service', 'skills']
        follow_exclude = ['service_provider_id', 'trash', 'service_id', 'id']
        exclude = ['id', 'trash']
        fk = ['service_id', ]


class ServiceSkill(db.Base):
    __tablename__ = 'service_skill'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256), nullable=False)
    inspection = Column("inspection", Boolean, default=False)
    service_provider_id = Column("service_provider_id", ForeignKey('service_provider.id'))
    service_id = Column("service_id", ForeignKey('service.id'))
    trash = Column('trash', Boolean, default=False)

    class Meta(object):
        follow = []
        follow_exclude = []
        exclude = []
        fk = []


class Job(db.Base):
    __tablename__ = 'job'

    status_enums = ('assigned', 'quoted', 'started', 'complete')

    id = Column(Integer, primary_key=True)
    status = Column("status", Enum(*status_enums, name='status_types'), default='assigned')
    service_provider_id = Column("service_provider_id", ForeignKey('service_provider.id'))
    service_id = Column("service_id", ForeignKey("service.id"))
    user_id = Column("user_id", ForeignKey("user.id"))
    location = Column("location", ARRAY(Float, dimensions=1))
    request = Column("request", String(2048))
    address = Column("address", String(2048))
    phone_number = Column("phone_number", String(20))
    inspection = Column("inspection", Boolean, default=False)
    appointment_time = Column("appointment_time", DateTime(timezone=True))
    quote = Column("quote", Float)
    quoted_duration = Column("quoted_duration", Float)
    started = Column("started", DateTime(timezone=True))
    ended = Column("ended", DateTime(timezone=True))
    materials_required = Column("materials_required", Boolean, default=False)

    class Meta(object):
        follow = ['service', 'service_provider']
        exclude = ['id', 'trash']
        follow_exclude = []
        fk = ['service_id', 'service_provider_id']


class User(db.Base):
    __tablename__ = 'user'

    user_types = ('admin', 'user')

    id = Column(Integer, primary_key=True)
    user_type = Column("user_type", Enum(*user_types, name='user_types'), default='user')
    name = Column("name", String(1024), nullable=False)
    email = Column("email", String(256), nullable=False)
    phone_number = Column("phone", String(20), nullable=False)
    location = Column("location", ARRAY(Float, dimensions=1))
    _password = Column("password", String(80))
    address = Column("address", String(2048))
    jobs = relationship("Job", backref=backref("user"))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        bcrypt = BCRYPTPasswordManager()
        self._password = unicode(bcrypt.encode(raw_password, rounds=12))

    def check_password(self, password):
        bcrypt = BCRYPTPasswordManager()
        return bcrypt.check(self.password, password)
