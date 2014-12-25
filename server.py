from tornado import ioloop

from admin import admin_application


if __name__ == "__main__":
    admin_application.listen(8888)
    ioloop.IOLoop.instance().start()

