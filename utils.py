import json
import datetime
import decimal
import random

from sqlalchemy.orm.query import Query
from tornado.web import authenticated
from tornado.web import HTTPError
from functools import wraps

import db

from exc import AppException

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
def allow(*user_types, **basekw):
    """allow decorator usage:
        @allow('admin') --> allows only admin users for non base resources
        @allow('service_provider', 'admin') --> allows only service provider
            and admin users for non base resources
        @allow('service_provider', base=True) --> allows only service provider
            user for base resources
        @allow('service_provider', 'service_user', 'admin', base=True) --> allows
            service provider, service user and admin user for baser resources
    """
    allowed_user_types = {'service_user', 'service_provider', 'admin'}
    if not set(user_types) <= allowed_user_types:
        raise AppException('only su/sp/admin allowed')

    def validate(function):
        @wraps(function)
        def _wrapper(self, *args, **kwargs):

            if not self.current_user:
                raise HTTPError(401, reason='not logged in')
            user_type = self.session['user_type']
            buid = self.session['buid']
            uid = self.session['uid']
            kwargs['user_type'] = user_type
            kwargs['buid'] = buid
            kwargs['uid'] = uid
            base = basekw.get('base', False)
            allow_list = basekw.get('allow_list', False)
            post_pk = basekw.get('post_pk', False)
            if user_type not in user_types:
                raise HTTPError(403, reason='user not allowed to access resource')

            if self.request.method == 'GET':
                if base:
                    kwargs['pk'] = uid
                if not allow_list and not kwargs['pk']:
                    raise HTTPError(403, reason='cannot access resource without pk')

            elif self.request.method in ("PUT", "DELETE"):
                if base:
                    kwargs['pk'] = uid
                if not kwargs['pk']:
                    raise HTTPError(403, reason='cannot update resource without pk')

            elif self.request.method == 'POST':
                if base and not kwargs['pk']:
                    kwargs['pk'] = uid
                if kwargs['pk']:
                    kwargs['pk'] = kwargs['pk'].strip('/')
                if kwargs['pk'] and not post_pk:
                    raise HTTPError(403, reason='cannot post with pk')

            return function(self, *args, **kwargs)
        return _wrapper

    return validate
