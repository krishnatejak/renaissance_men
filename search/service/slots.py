import datetime

def get_available_slots(redis, service, duration):
    #sps = redis.smembers("services:{0}:sps".format(service))
    #self.r.zadd("{0}:availability:sps".format(service), (0, 1))

    # Getting the service providers who are available
    # in this service to use for zuninionstore.
    sp_list = redis.ZRANGEBYSCORE("{0}:availability:sps".format(service), 1, 1)
    redis.zunionstore('final_slots', list(sp_list))
    free_slots = redis.zrange('final_slots', 0, -1)
    slots_duration = [slot for slot in range(free_slots, step=duration/5)]

    #Todo Got the slot durations as per 30 minute interval. Now we have to construct the message::
    #The times are in UTC.
    # 		{
    #		  "date": "2015-03-01",
    #		  "available": true,
    #		  "timeslots": [
    #		    {
    #		      "name": 1425234600,
    #		      "display": "10:30am",
    #		      "available": true,
    #		      "schedule_start_at": 1425234600,
    #		      "schedule_end_at": 1425236400
    #		    },
    #		    {
    #		      "name": 1425236400,
    #		      "display": "11:00am",
    #		      "available": true,
    #		      "schedule_start_at": 1425236400,
    #		      "schedule_end_at": 1425238200
    #		    }
    #		  ]
    #		}


    date = datetime.datetime.now()
    return_list = {
        'date' : date.strftime('%Y-%m-%d')
    }
