from tornado import ioloop

from admin import admin_application
from search import search_application
from jobs import job_application


if __name__ == "__main__":
    admin_application.listen(8888)
    search_application.listen(8889)
    job_application.listen(8887)
    ioloop.IOLoop.instance().start()

