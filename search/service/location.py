from exc import AppException
from geopy.geocoders.googlev3 import GoogleV3

def is_location_serviced(**kwargs):
    """expects either location as [lat,long] or address"""
    if 'location' in kwargs:
        pass
    elif 'address' in kwargs:
        pass
    else:
        raise AppException('location or address needed')