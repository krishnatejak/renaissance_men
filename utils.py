import json
import datetime
import decimal


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
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
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


def model_to_dict(model_obj, uri):
    models_dict = model_obj.asdict(
        exclude=model_obj.Meta.exclude + model_obj.Meta.fk,
        follow={
            e: dict(exclude=model_obj.Meta.exclude)
            for e in model_obj.Meta.follow
        }
    )
    models_dict['href'] = {
        'url': '/%s/%d' % (uri, model_obj.id)
    }
    return models_dict