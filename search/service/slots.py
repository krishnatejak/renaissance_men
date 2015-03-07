import datetime
import constants
import pytz


def get_available_slots(redis, service):
    utcnow = datetime.datetime.utcnow()
    tz = pytz.utc
    available_slots = []
    for day in range(3):
        time_slots = []
        duration = constants.SLOT_DEFAULT_DURATION[service]/5
        base_datetime = datetime.datetime(utcnow.year, utcnow.month, utcnow.day, tzinfo=tz)
        base_datetime = base_datetime + datetime.timedelta(days=day)
        for slot in range(0, 288, duration):
            time_slots.append({
                "available": False,
                "schedule_start_at": get_datetime_for_slot(slot, base_datetime),
                "schedule_end_at": get_datetime_for_slot(slot + duration, base_datetime)
            })

        if day == 0:
            sp_list = redis.zrangebyscore(
                "{0}:availability:sps".format(service), 1, 1
            )
        else:
            sp_list = sp_list = redis.zrangebyscore(
                "{0}:availability:sps".format(service), 0, 1
            )
        md = base_datetime.strftime('%m%d')
        available = False
        if sp_list:
            redis.zunionstore('free_slots', [
                'schedule:{0}:{1}'.format(sp, md) for sp in sp_list
            ])
            available = redis.zcard('final_slots') > 0
            free_slots = redis.zrange('final_slots', 0, -1)
            for free_slot in free_slots:
                time_slots[free_slot]['available'] = True
        available_slots.append({
            "date": base_datetime,
            "available": available,
            "timeslots": time_slots
        })
    return available_slots


def get_datetime_for_slot(slot, base_datetime):
    td = datetime.timedelta(minutes=slot * 5)
    return base_datetime + td
