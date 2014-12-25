from tornado import ioloop

from admin import admin_application
from search import search_application


if __name__ == "__main__":
    admin_application.listen(8888)
    search_application.listen(8889)
    ioloop.IOLoop.instance().start()

