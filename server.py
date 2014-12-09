import sys
import os

from tornado import ioloop, web
from serviceprovider import service_provider

#sys.path.append(os.path.abspath('.'))



if __name__ == "__main__":
    service_provider.listen(8888)
    ioloop.IOLoop.instance().start()

