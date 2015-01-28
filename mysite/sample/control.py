from django.conf import settings
# get qingcloud python sdk from https://github.com/yunify/qingcloud-sdk-python
from qingcloud.app.connection import AppConnection
from qingcloud.conn.auth import AppSignatureAuthHandler

class AuthException(Exception):
    pass

class QcControl:

    def __init__(self, payload, signature):
        print settings
        auth = AppSignatureAuthHandler(settings.APP_ID,
                                       settings.SECRET_APP_KEY)

        access_info = auth.extract_payload(payload, signature)
        if not access_info:
            raise AuthException("Incorrect signature")

        self.zone = access_info["zone"]
        self.conn = AppConnection(settings.APP_ID,
                                  settings.SECRET_APP_KEY,
                                  access_info["zone"],
                                  access_token=access_info["access_token"])

    def get_user_info(self):
        return self.conn.describe_users()
        