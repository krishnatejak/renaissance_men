import plivo

import config


class Sms(object):
    def __init__(self, to_number):
        self.auth_id = config.PLIVO_AUTH_ID
        self.auth_token = config.PLIVO_AUTH_TOKEN
        self.from_number = config.PLIVO_NUMBER
        self.to_number = to_number
        self.body = None

    def generate_sms_body(self):

        raise NotImplementedError

    def send_sms(self):
        self.generate_sms_body()
        try:
            plivo_client = plivo.RestAPI(self.auth_id, self.auth_token)

            message = {
                'src': self.from_number,
                'dst': self.to_number,
                'text': self.body,
            }
            message_delivered = plivo_client.send_message(message)
        except Exception as e:
            raise e


class OtpSms(Sms):
    def __init__(self, to_number, body):
        self.sms_body = body
        super(OtpSms, self).__init__(to_number=to_number)

    def generate_sms_body(self):
        self.body = self.sms_body
