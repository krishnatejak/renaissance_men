import datetime

import pytz

import constants
from utils import parse_json_datetime
from exc import AssignmentException

def get_available_slots(redis, service):
    utcnow = datetime.datetime.utcnow()
    tz = pytz.utc
    available_slots = []
    for day in range(3):
        time_slots = []
        duration = constants.SLOT_DEFAULT_DURATION[service] / 5
        base_datetime = datetime.datetime(utcnow.year, utcnow.month, utcnow.day,
                                          tzinfo=tz)
        base_datetime = base_datetime + datetime.timedelta(days=day)
        for slot in range(0, 288, duration):
            time_slots.append({
                "available": False,
                "schedule_start_at": get_datetime_for_slot(slot, base_datetime),
                "schedule_end_at": get_datetime_for_slot(slot + duration,
                                                         base_datetime)
            })

        if day == 0:
            sp_list = redis.zrangebyscore(
                "{0}:availability:sps".format(service), 1, 1
            )
        else:
            sp_list = redis.zrangebyscore(
                "{0}:availability:sps".format(service), 0, 1
            )
        md = base_datetime.strftime('%m%d')
        available = False
        if sp_list:
            redis.zunionstore('free_slots', [
                'schedule:{0}:{1}'.format(sp, md) for sp in sp_list
            ])
            available = redis.zcard('free_slots') > 0
            free_slots = redis.zrange('free_slots', 0, -1)
            free_slots = [
                int(free_slot) / duration for i, free_slot in
                enumerate(free_slots)
                if not i % duration
            ]
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


def block_slot(redis, service, slot_datetime):
    """blocks given slot for service, return True/False"""
    slot_datetime = parse_json_datetime(slot_datetime)
    md = slot_datetime.strftime('%m%d')
    slot = (slot_datetime.hour * 60 + slot_datetime.minute)/5
    count = redis.hmget("schedule:block", "{0}:{1}:{2}".format(service, md, slot))


def assign_slot_to_sp(redis, service, slot_datetime):
    """assigns slot to sp for service, returns sp id if assigned,
     raises AssignmentException otherwise"""
    slot_datetime = parse_json_datetime(slot_datetime)

    utcnow = datetime.datetime.utcnow()
    if slot_datetime < utcnow:
        raise AssignmentException('Cannot assign slot in past')

    utcnow3 = datetime.datetime(utcnow.year, utcnow.month, utcnow.day + 3)
    if slot_datetime > utcnow3:
        raise AssignmentException('Cannot assign slot 3 days into future')

    if slot_datetime.day == utcnow.day:
        sp_list = redis.zrangebyscore(
            "{0}:availability:sps".format(service), 1, 1
        )
    else:
        sp_list = redis.zrangebyscore(
            "{0}:availability:sps".format(service), 0, 1
        )
    md = slot_datetime.strftime('%m%d')
    slot = (slot_datetime.hour * 60 + slot_datetime.minute)/5
    duration = constants.SLOT_DEFAULT_DURATION[service]/5
    slot_end = slot + duration -1

    for sp in sp_list:
        slots = redis.zrangebyscore(
            'schedule:{0}:{1}'.format(sp, md), slot, slot_end
        )
        if slots:
            if len(slots) == duration:
                redis.zremrangebyscore(
                    'schedule:{0}:{1}'.format(sp, md), slot, slot_end
                )
                return sp
    raise AssignmentException('slot not available')
