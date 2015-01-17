from search import tasks
import config

def search(redis, service, skill,latitude, longitude, session):
    try:
        if latitude and longitude:
            tasks.get_sp_within_distance.apply_async(
                args=(service,latitude,longitude, session),
                queue=config.SEARCH_GET_DISTANCE_QUEUE
            )
        if not service:
            services = list(redis.smembers("services"))
            service_dict = {'services':services}
            return service_dict
        elif not skill:
            skills = redis.smembers("{0}:skills".format(service))
            skills_list = list(skills)
            return {service:skills_list}
        else:
            sps = redis.hget(session,'search_id:{0}'.format(service))
            service_providers = sps.split(',')
            sp_list = []
            for provider_id in service_providers:
                skills = list(redis.smembers("sp:{0}:{1}:skills".format(provider_id,service)))
                sp_dict = {}
                if skill in skills:
                    sp_keys = list(redis.hgetall("sp:{0}".format(provider_id)))
                    for sp_key in sp_keys:
                        sp_dict.update({sp_key: redis.hget("sp:{0}".format(provider_id),sp_key)})
                    sp_list.append(sp_dict)

            return_dict = {'service_providers' : sp_list}
            return return_dict
    except Exception as e:
        raise e