from tornado import ioloop

from admin import service_provider


if __name__ == "__main__":
    service_provider.listen(8888)
    ioloop.IOLoop.instance().start()

