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
SESSION_HEADER = 'X-Session-ID'

# Task Queues
SERVICE_PROVIDER_QUEUE = 'admin.serviceprovider'
SERVICE_QUEUE = 'admin.service'
JOB_QUEUE = 'admin.job'
USER_QUEUE = 'admin.user'
SEARCH_GET_DISTANCE_QUEUE = 'search.getdistances'

TWILIO_ACCOUNT_SID = 'AC6193f21a81db598c4e385ca160dd1594'
TWILIO_AUTH_TOKEN = '0c91e2dc901fba5d1a1cf1b1de02c107'
TWILIO_FROM_NUMBER = '+19375021395'

# Google OAuth credentials
GOOGLE_OAUTH2_CLIENT_SECRET = '_IrSZMA2a6uweNyUdXZA-KEz '
GOOGLE_OAUTH2_CLIENT_ID = '1003714066979-0jut8h3vr7kf3t44bia55k45nbpmv1pg.apps.googleusercontent.com'

# Auth redirect urls
GOOGLE_OAUTH_SP_REDIRECT = 'https://accurox.com/api/serviceprovider/auth/google/'
GOOGLE_OAUTH_USER_REDIRECT = 'https://accurox.com/api/user/auth/google/'

#Google API Key
GOOGLE_GCM_API_KEY = 'AIzaSyBs0_M1TNHMMkIVv6k4-kcGJsrRYsUHm5Y'
