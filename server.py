import sys
import os

from tornado import httpserver, ioloop, web


sys.path.append(os.path.abspath('.'))

from api.search import Search


if __name__ == "__main__":
    application = web.Application([
                                      (r'/', Search),
                                  ], **{})

    http_server = httpserver.HTTPServer(application)
    http_server.listen(get_sys_config('AppPort'))
    ioloop.IOLoop.instance().start()
