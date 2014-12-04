import os
import ConfigParser

CONFIG = ConfigParser.ConfigParser()
# list all possible config file locations, unavailable locations are silently ignored
CONFIG.read(
    (
        #'/opt/wapp/conf/config.ini',
        os.path.join(os.path.abspath('renaissance_men'),
         'ext_config/config.ini')

    )
)

def get_sys_config(prop, label='DEFAULT'):
    try:
        return CONFIG.get(label, prop)
    except:
        return None