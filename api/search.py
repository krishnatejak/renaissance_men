import sys

import tornado.web
from tornado import gen
from geopy.distance import vincenty,great_circle
import simplejson,urllib

sys.path.append('../../')

class Search(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        self.finish()

    @gen.engine
    def getDistance(self,orig_coord,dest_coord):
        orig_coord = 12.914611,77.585834
        dest_coord = 12.872610,77.571500
        distance = vincenty(orig_coord, dest_coord).kilometers
        return distance
        ### Calculating exact distance from google maps ###
        #url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_coord),str(dest_coord))
        #result= simplejson.load(urllib.urlopen(url))
        #distance = result['rows'][0]['elements'][0]['distance']['value']
