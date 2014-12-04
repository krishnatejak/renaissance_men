import sys
import os
from tornado import httpserver,ioloop,web

sys.path.append(os.path.abspath('.'))

from renaissance_men.cmn_infra.config import get_sys_config
from renaissance_men.api.search import Search

if __name__ == "__main__":
    application = web.Application([
        (r'/', Search),
                ],**{})

    http_server = httpserver.HTTPServer(application)
    http_server.listen(get_sys_config('AppPort'))
    ioloop.IOLoop.instance().start()
