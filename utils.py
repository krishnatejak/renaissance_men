import json
import datetime
import decimal
import random

from sqlalchemy.orm.query import Query
from tornado.web import authenticated
from tornado.web import HTTPError
from functools import wraps

import db

CHARACTER_POOL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+=-'

JSON_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is not None and value.tzinfo.utcoffset(
        value) is not None


class TornadoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            '''
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            '''
            return o.strftime('%s')
        elif isinstance(o, datetime.date):
            #return o.isoformat()
            return o.strftime('%s')
        elif isinstance(o, datetime.time):
            '''
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
            '''
            return o.strftime('%s')
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(TornadoJSONEncoder, self).default(o)


def transaction(function):
    """transaction decorator to handle session life cycle"""
    def _wrapper(session, *args, **kwargs):
        try:
            return function(session, *args, **kwargs)
        except:
            session.rollback()
            raise
        finally:
            pass
            #session.close()

    return _wrapper


def update_model_from_dict(model_instance, value_dict):
    for key, value in value_dict.iteritems():
        if hasattr(model_instance, key):
            setattr(model_instance, key, value)


def model_to_dict(instance_or_query, response_uris, uri_kwargs):
    if isinstance(instance_or_query, Query):
        models_list = []
        response_dict = {
            'meta': {},
            'objects': models_list
        }
        for instance in instance_or_query:
            models_dict = instance.asdict(
                exclude=instance.Meta.exclude + instance.Meta.fk,
                follow={
                    e: dict(exclude=instance.Meta.follow_exclude)
                    for e in instance.Meta.follow
                }
            )
            #uri_kwargs['id'] = instance.id
            #model_urls = {
            #    k: v.format(**uri_kwargs)
            #    for k, v in response_uris.iteritems()
            #}
            #models_dict['urls'] = model_urls
            models_list.append(models_dict)
        return response_dict
    elif isinstance(instance_or_query, db.Base):
        models_dict = instance_or_query.asdict(
            exclude=instance_or_query.Meta.exclude + instance_or_query.Meta.fk,
            follow={
                e: dict(exclude=instance_or_query.Meta.follow_exclude)
                for e in instance_or_query.Meta.follow
            }
        )
        #uri_kwargs['id'] = instance_or_query.id
        #model_urls = {
        #    k: v.format(**uri_kwargs)
        #    for k, v in response_uris.iteritems()
        #}
        #models_dict['urls'] = model_urls
        return models_dict


def generate_secret(length=32):

    return ''.join(random.choice(CHARACTER_POOL) for i in range(length))


def parse_json_datetime(datetime_string):
    datetime_string = datetime_string.strip()
    return datetime.datetime.strptime(datetime_string, JSON_DATETIME_FORMAT)


def get_json_datetime(date_time=None):
    if not date_time:
        now = datetime.datetime.now()
        return now.strftime(JSON_DATETIME_FORMAT)
    return date_time.strftime(JSON_DATETIME_FORMAT)

def parse_datetime(epoch_time):
    #date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(epoch_time)))
    date_time = datetime.datetime.fromtimestamp(float(epoch_time))
    return date_time

# authorization methods
def sp(function):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise HTTPError(401)
        if not self.session['user_type'] == 'service_provider':
                raise HTTPError(403)
        if self.request.method in ("GET", "PUT", "DELETE"):
            spid = kwargs['id'] if 'id' in kwargs else args[0]
            if self.session['uid'] != spid:
                raise HTTPError(403)
        if self.request.method == "POST":
            if kwargs.get('id') or args:
                raise HTTPError(403)
        return function(self, *args, **kwargs)
    return wrapper


def su(function):
    @wraps(function)
    @authenticated
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise HTTPError(401)
        if not self.session['user_type'] == 'service_user':
                raise HTTPError(403)
        if self.request.method in ("GET", "PUT", "DELETE"):
            spid = kwargs['id'] if 'id' in kwargs else args[0]
            print self.session['uid']
            if self.session['uid'] != spid:
                raise HTTPError(403)
        if self.request.method == "POST":
            if kwargs.get('id') or args:
                raise HTTPError(403)
        return function(self, *args, **kwargs)
    return wrapper


def admin(function):
    pass
