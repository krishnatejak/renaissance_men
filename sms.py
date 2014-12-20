import plivo
import config



class SMS(object):
    def __init__(self, *args, **kwargs):
        self.auth_id = config.PLIVO_AUTH_ID
        self.auth_token = config.PLIVO_AUTH_TOKEN
        self.from_number = config.PLIVO_NUMBER
        self.to_number = kwargs.get('to_number')
        self.body = None

    def generate_sms_body(self):

        raise NotImplementedError

    def send_sms(self):
        self.generate_sms_body()
        try:
            plivio_client = plivo.RestAPI(self.PLIVO_AUTH_ID, self.PLIVO_AUTH_TOKEN)

            message = {
              'src':self.PLIVO_NUMBER,
              'dst':self.to_number,
              'text':self.body,
            }
            message_delivered = plivio_client.send_message(message)
        except Exception as e:
            raise e



class OTPSMS(SMS):
    def __init__(self, to_number,body):
        self.sms_body = body
        super(OTPSMS, self).__init__(to_number=to_number)

    def generate_sms_body(self):
        self.body = self.sms_body
