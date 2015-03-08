from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from tornado.web import HTTPError
import traceback
import logging


class AppException(Exception):
    pass


class AssignmentException(Exception):
    pass

def handle_exceptions(function):
    def _wrapper(instance, *args, **kwargs):
        try:
            return function(instance, *args, **kwargs)
        except AppException as ae:
            logging.warn(traceback.format_exc())
            instance.set_status(400)
            instance.write({
                'error': str(ae)
            })
            instance.flush()
        except (NoResultFound, MultipleResultsFound):
            logging.warn(traceback.format_exc())
            instance.set_status(400)
            instance.write({
                'error': 'No results found'
            })
            instance.flush()
        except HTTPError as he:
            logging.warn(traceback.format_exc())
            raise he
        except Exception as e:
            logging.warn(traceback.format_exc())
            instance.set_status(500)
            instance.write({
                'error': str(e)
            })
            instance.flush()
    return _wrapper
