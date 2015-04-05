import traceback
import logging
from functools import wraps

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from tornado.web import HTTPError


class AppException(Exception):
    pass


class AssignmentException(Exception):
    pass


def handle_exceptions(function):
    """usage: should decorate verbs on handlers"""

    @wraps(function)
    def _wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except (AppException, AssignmentException) as ae:
            logging.warn(traceback.format_exc())
            self.set_status(400)
            self.write({
                'error': str(ae)
            })
            self.flush()
        except (NoResultFound, MultipleResultsFound):
            logging.warn(traceback.format_exc())
            self.set_status(404)
            self.write({
                'error': 'No results found'
            })
            self.flush()
        except HTTPError as he:
            logging.warn(traceback.format_exc())
            self.set_status(he.status_code)
            self.write({
                'error': he.reason
            })
            self.flush()
        except Exception as e:
            logging.warn(traceback.format_exc())
            self.set_status(500)
            self.write({
                'error': str(e)
            })
            self.flush()

    return _wrapper
