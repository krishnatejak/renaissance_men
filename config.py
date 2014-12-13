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
        'port': '6379'
    }
}

OTP_SECRET = '7TT3WCJF7OIEKNYLMJSXWS3BV76RB3GI'

DEBUG = True