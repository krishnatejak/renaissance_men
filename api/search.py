import sys

import tornado.web
from tornado import gen


sys.path.append('../../')


class Search(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        self.write('successful')
        self.finish()