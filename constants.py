import pytz
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')
GMT_TIMEZONE = pytz.utc

ALLOWED_SERVICES = ('laundry', 'plumber', 'electrician', 'cook')
SLOT_NO_OF_DAYS = 3
SLOT_DAY_END_HOUR = 19
SLOT_DEFAULT_DURATION = {
    "laundry": 30,
    "plumber": 30,
    "electrician": 30,
    "cook": 30
}

SUPPORT_EMAIL_ADDRESS = 'contact@sevame.in'

ORDER_ACCEPTED_SUBJECT = 'Order has been successfully placed.'
LAUNDRY_BILL_EMAIL_SUBJECT = 'Order has been picked up'
FEEDBACK_SUBJECT = 'Order completed.'
QUOTE_OTHERS = 'Quote Estimate for {0} Order No {1}'
SP_ASSIGNED = '{0}, {1} is on his way.'

FEEDBACK_LINK = ""

DEFAULT_SP_IMAGE = "https://s3-us-west-2.amazonaws.com/sevame/documents/sp.png"
