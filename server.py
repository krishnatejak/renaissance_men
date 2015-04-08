from tornado import ioloop

from admin import admin_application
from search import search_application

import tornado.httpclient
# setting http request default timeout to 58 seconds to match nginx timeout
# allowing two seconds to send response back to nginx to clean up files
tornado.httpclient.HTTPRequest._DEFAULTS['request_timeout'] = 58.0


if __name__ == "__main__":
    admin_application.listen(8888)
    search_application.listen(8889)
    ioloop.IOLoop.instance().start()

