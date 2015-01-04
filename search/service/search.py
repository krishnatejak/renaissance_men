


def search(redis, service, skill):
    try:
        if not service:
            services = list(redis.smembers("services"))
            service_dict = {'services':services}
            return service_dict
        elif not skill:
            skills = redis.smembers("{0}:skills".format(service))
            skills_list = list(skills)
            return {service:skills_list}
        else:
            service_providers = list(redis.smembers("{0}:providers".format(service)))
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