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
        'max_connections': 2000
    }
}

OTP_SECRET = '7TT3WCJF7OIEKNYLMJSXWS3BV76RB3GI'

CELERY_BROKER = 'amqp://guest:guest@localhost:5672//'

DEBUG = True

PLIVO_AUTH_ID = 'MAY2UWODK4MWVHM2E3NJ'
PLIVO_AUTH_TOKEN = 'YTljZjY2YTk4NTg1MmZhNDY4NjY2MjI1MWY1ZWM2'
PLIVO_NUMBER = ''
