import json
from sqlalchemy.orm import sessionmaker, scoped_session
from serviceprovider.models import *


def get_service_provider(dbsession, provider_id):
    dbsession.query(ServiceProvider).filter_by(
        id=provider_id, trash=False
    ).one()

def get_service_providers(dbsession):
    dbsession.query(ServiceProvider)

def create_service_provider(engine, post_data):
    try:
        dbsession = scoped_session(sessionmaker(bind=engine))
        service_name = post_data.pop('service_name').lower()
        service = dbsession.query(Service).filter(Service.name==service_name).one()

        service_provider = ServiceProvider()
        #json.dumps(cls=T)
        update_object(service_provider,post_data)
        service_provider.service = service.id
        dbsession.add(service_provider)
        dbsession.commit()
        return_dict = service_provider.asdict()
        return_dict['service'] = service.asdict()

        data = {"response_code":200, 'data':return_dict}
    except Exception as e:
        print e
        data = {'response_code':400,'data':''}

    return data


def update_object(model_obj, value_dict):
    for key in value_dict:
        setattr(model_obj, key, value_dict.get(key))

def object_to_dict(model_obj):
    return_dict = {}
    for column in model_obj.__table__.columns:
        return_dict[column.name] = getattr(model_obj,column.name)

    return return_dict
