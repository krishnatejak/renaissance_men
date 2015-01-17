from background import celery
from background import DBTask

from geopy.distance import vincenty

@celery.task(name='search.get_sp_within_distance', base=DBTask, bind=True)
def get_sp_within_distance(self, service, latitude, longitude, session):

    dest_cord = [latitude, longitude]
    service_providers = self.r.smembers("{0}:providers".format(service))
    sps = ''
    for service_provider in service_providers:
        sp = self.r.hgetall("sp:{0}".format(service_provider))
        if sp.get('availability') == 'True':
            sp_coord = sp.get('office_location')
            distance = vincenty(sp_coord, dest_cord).kilometers
            if int(distance) < int(sp.get('service_range')):
                if sps:
                    sps = sps + ',' + service_provider
                else:
                    sps = service_provider
    self.r.hset(session,'search_id:{0}'.format(service),sps)