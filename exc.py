from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class AppException(Exception):
    pass


def handle_exceptions(function):
    def _wrapper(instance, *args, **kwargs):
        try:
            return function(instance, *args, **kwargs)
        except AppException as ae:
            instance.set_status(400)
            instance.write({
                'error': str(ae)
            })
            instance.flush()
        except (NoResultFound, MultipleResultsFound):
            instance.set_status(400)
            instance.write({
                'error': 'No results found'
            })
            instance.flush()
        except Exception as e:
            instance.set_status(500)
            instance.write({
                'error': str(e)
            })
            instance.flush()
    return _wrapper