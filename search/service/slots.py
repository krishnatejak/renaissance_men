import datetime

import constants
from utils import parse_datetime
from exc import AssignmentException


def get_available_slots(redis, service):
    now = datetime.datetime.now()
    base_datetime = datetime.datetime(now.year, now.month, now.day)
    base_datetime = constants.IST_TIMEZONE.localize(base_datetime)
    available_slots = []
    # if after 10 PM don't show today's slot
    start = 1 if now.hour > constants.SLOT_DAY_END_HOUR else 0
    for day in range(start, constants.SLOT_NO_OF_DAYS):
        time_slots = []
        duration = constants.SLOT_DEFAULT_DURATION[service] / 5
        day_start = base_datetime + datetime.timedelta(days=day)
        for slot in range(0, 288, duration):
            time_slots.append({
                "available": False,
                "schedule_start_at": get_datetime_for_slot(slot, day_start),
                "schedule_end_at": get_datetime_for_slot(slot + duration,
                                                         day_start)
            })
        if day == 0:
            sp_list = redis.zrangebyscore(
                "{0}:availability:sps".format(service), 1, 1
            )
        else:
            sp_list = redis.zrangebyscore(
                "{0}:availability:sps".format(service), 0, 1
            )
        md = day_start.strftime('%m%d')
        available = False
        if sp_list:
            redis.zunionstore('free_slots', [
                'schedule:{0}:{1}'.format(sp, md) for sp in sp_list
            ])
            available = redis.zcard('free_slots') > 0
            free_slots = redis.zrange('free_slots', 0, -1)
            print free_slots
            if day == 0:
                interval = (now.hour * 60 + now.minute)/5 + 36
                free_slots = [
                    int(free_slot)/duration for free_slot in
                    free_slots
                    if not int(free_slot) % duration and int(free_slot) > interval
                ]
            else:
                free_slots = [
                    int(free_slot)/duration for free_slot in
                    free_slots
                    if not int(free_slot) % duration
                ]
            for free_slot in free_slots:
                time_slots[free_slot]['available'] = True
        available_slots.append({
            "date": day_start,
            "available": available,
            "timeslots": time_slots
        })

    return available_slots


def get_datetime_for_slot(slot, base_datetime):
    td = datetime.timedelta(minutes=slot * 5)
    return base_datetime + td


def block_slot(redis, service, slot_datetime):
    """blocks given slot for service, return True/False"""
    slot_datetime = parse_datetime(slot_datetime)
    md = slot_datetime.strftime('%m%d')
    slot = (slot_datetime.hour * 60 + slot_datetime.minute)/5
    count = redis.hmget("schedule:block", "{0}:{1}:{2}".format(service, md, slot))


def assign_slot_to_sp(redis, service, slot_datetime, block=False):
    """assigns slot to sp for service, returns sp id if assigned,
     raises AssignmentException otherwise"""
    slot_datetime = parse_datetime(slot_datetime)
    now = datetime.datetime.now()
    if slot_datetime < now + datetime.timedelta(hours=2):
        raise AssignmentException('Cannot assign slot in past')

    now3 = datetime.datetime(now.year, now.month, now.day + 3)
    if slot_datetime > now3:
        raise AssignmentException('Cannot assign slot 3 days into future')

    if slot_datetime.day == now.day:
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
            if len(slots) == duration and not block:
                redis.zremrangebyscore(
                    'schedule:{0}:{1}'.format(sp, md), slot, slot_end
                )
                return sp
    raise AssignmentException('slot not available')
