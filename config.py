DATABASES = {
    'default': {
        'ENGINE': 'postgresql+psycopg2',
        'NAME': 'renaissance',
        'USER': 'renaissanceman',
        'PASSWORD': 'reddecemberwindows',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'redis': {
        'host': 'localhost',
        'port': '6379',
    }
}

OTP_SECRET = '7TT3WCJF7OIEKNYLMJSXWS3BV76RB3GI'
COOKIE_SECRET = 'qsW+SmlyTnac8FHu/iLZDXKepPtAkkIDhmkLbj+AQlQ='
CELERY_BROKER = 'amqp://guest:guest@localhost:5672//'

DEBUG = True

# Session settings
SESSION_PREFIX = 'session'
SESSION_EXPIRY = 30  # in days
SESSION_COOKIE_NAME = 'sid'

# Task Queues
SERVICE_PROVIDER_QUEUE = 'admin.serviceprovider'
SERVICE_QUEUE = 'admin.service'
JOB_QUEUE = 'admin.job'
USER_QUEUE = 'admin.user'

PLIVO_AUTH_ID = 'MAY2UWODK4MWVHM2E3NJ'
PLIVO_AUTH_TOKEN = 'YTljZjY2YTk4NTg1MmZhNDY4NjY2MjI1MWY1ZWM2'
PLIVO_NUMBER = ''
