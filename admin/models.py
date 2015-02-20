from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy import DateTime, Enum
from sqlalchemy.dialects.postgres import ARRAY
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import db

__all__ = ['Service', 'ServiceProvider', 'Job', 'ServiceSkill', 'BaseUser',
           'ServiceUser']


class Service(db.Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256), nullable=False)
    jobs = relationship('Job', backref=backref('service'))
    skills = relationship('ServiceSkill', backref=backref('service'))
    trash = Column("trash", Boolean, default=False)

    class Meta(object):
        follow = ['skills']
        follow_exclude = ['service_provider_id', 'trash', 'service_id', 'id', 'inspection']
        exclude = ['trash']
        fk = []


class ServiceSkill(db.Base):
    __tablename__ = 'service_skill'

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256), nullable=False)
    inspection = Column("inspection", Boolean, default=False)
    service_id = Column("service_id", ForeignKey('service.id'))
    trash = Column('trash', Boolean, default=False)

    class Meta(object):
        follow = []
        follow_exclude = []
        exclude = ['id', 'trash']
        fk = []


class ServiceProviderSkill(db.Base):
    __tablename__ = 'service_provider_skill'

    id = Column(Integer, primary_key=True)
    service_provider_id = Column('service_provider_id', Integer, ForeignKey('service_provider.id'))
    service_skill_id = Column('service_skill_id', Integer, ForeignKey('service_skill.id'))


class ServiceProvider(db.Base):
    __tablename__ = 'service_provider'

    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", ForeignKey('base_user.id'))
    availability = Column("availability", Boolean, default=False)
    home_location = Column("home_location", ARRAY(Float, dimensions=1))
    office_location = Column("office_location", ARRAY(Float, dimensions=1))
    cost = Column("cost", Float, default=0.0)
    experience = Column("experience", Float, default=0.0)
    jobs = relationship('Job', backref=backref('service_provider'))
    orders = relationship('Order', backref=backref('service_provider'))
    service_range = Column("service_range", Integer, default=5)
    trash = Column("trash", Boolean, default=False)

    skills = relationship("ServiceSkill", secondary='service_provider_skill')

    class Meta(object):
        follow = ['user']
        follow_exclude = []
        exclude = ['trash', 'user_id']
        fk = []


class ServiceUser(db.Base):
    __tablename__ = 'service_user'

    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", ForeignKey('base_user.id'))
    location = Column("location", ARRAY(Float, dimensions=1))
    jobs = relationship('Job', backref=backref('service_user'))
    orders = relationship('Order', backref=backref('service_user'))

    class Meta(object):
        follow = ['user']
        follow_exclude = ['user_id']
        exclude = []
        fk = []

class BaseUser(db.Base):
    __tablename__ = 'base_user'

    id = Column(Integer, primary_key=True)
    admin = Column("admin", Boolean, default=False)
    name = Column("name", String(1024))
    email = Column("email", String(256), nullable=False, index=True)
    phone_number = Column("phone", String(20))
    address = Column("address", String(2048))
    verified = Column("verified", Boolean, default=False)
    gcm_reg_id = Column("gcm_reg_id", String)
    service_provider = relationship("ServiceProvider", backref="user")
    service_user = relationship("ServiceUser", backref="user")

    class Meta(object):
        follow = []
        follow_exclude = []
        exclude = []
        fk = []


class Job(db.Base):
    __tablename__ = 'job'

    status_enums = ('assigned', 'accepted', 'rejected', 'started', 'complete')

    id = Column(Integer, primary_key=True)
    status = Column("status", Enum(*status_enums, name='status_types'), default='assigned')
    service_provider_id = Column("service_provider_id", ForeignKey('service_provider.id'))
    service_id = Column("service_id", ForeignKey("service.id"))
    service_user_id = Column("service_user_id", ForeignKey("service_user.id"))
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
        follow = ['service', 'service_provider', 'user']
        exclude = ['trash']
        follow_exclude = []
        fk = ['service_id', 'service_provider_id', 'user_id']


class Signupemail(db.Base):
    __tablename__ = 'signupemail'

    id = Column(Integer, primary_key=True)
    email = Column("email", String(256), nullable=False)
    feedback = Column("feedback", String(2048))
    trash = Column("trash", Boolean, default=False)

    class Meta(object):
        follow = []
        follow_exclude = []
        exclude = ['id', 'trash']
        fk = []


class Order(db.Base):
    __tablename__ = 'order'

    status_types = ('created', 'processing', 'assigned', 'completed')

    id = Column(Integer, primary_key=True)
    service = Column("service", String(256))
    location = Column("location", ARRAY(Float, dimensions=1))
    status = Column("status", Enum(*status_types, name='order_status_types'), default='created')
    request = Column("request", String(2048))
    scheduled = Column("scheduled", DateTime(timezone=True))
    created = Column("created", DateTime(timezone=True), default=datetime.utcnow())
    completed = Column("completed", DateTime(timezone=True))
    address = Column("address", String(2048))
    service_user_id = Column("service_user_id", ForeignKey("service_user.id"))
    service_provider_id = Column("service_provider_id", ForeignKey("service_provider.id"))
    job_id = Column("job_id", ForeignKey("job.id"))

    class Meta(object):
        follow = []
        follow_exclude = []
        exclude = []
        fk = []