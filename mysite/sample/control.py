from django.conf import settings
# get qingcloud python sdk from https://github.com/yunify/qingcloud-sdk-python
from qingcloud.app.connection import AppConnection
from qingcloud.conn.auth import AppSignatureAuthHandler

class AuthException(Exception):
    pass

class QcControl:

    def __init__(self, payload, signature):
        auth = AppSignatureAuthHandler(settings.APP_ID,
                                       settings.SECRET_APP_KEY)

        self.req = auth.extract_payload(payload, signature)
        if not self.req:
            raise AuthException("Incorrect signature")

        self.zone = self.req["zone"]
        self.conn = self.get_connection(self.req.get("access_token"),
                                        self.zone)
        self.app_action = self.req["action"]
        self.is_notification = True
        self.handle_map = {
                          "view_app": self.view_app,
                          "install_app": self.install_app,
                          "uninstall_app": self.uninstall_app,
                          "suspend_resource": self.suspend_resource,
                          "resume_resource": self.resume_resource,
                          "terminate_resource": self.terminate_resource
                          }

    def handle(self):
        print "handle action of %s"%(self.app_action)
        self.handle_map[self.app_action]()
        
    def get_user_info(self):
        user_set = self.conn.describe_users()
        if user_set:
            return user_set['user_set'][0]
        return None

    def get_eips(self):
        return self.conn.describe_eips(status=["available", 
                                               "associated",
                                               "suspended"])

    def get_connection(self, access_token, zone):
        return AppConnection(settings.APP_ID,
                             settings.SECRET_APP_KEY,
                             zone,
                             access_token=access_token)

    def view_app(self):
        self.is_notification = False

    def install_app(self):
        # you can inital user management in this event
        # or leave it to view_app

        print "%s installed App"%self.req["user_id"]

    def uninstall_app(self):
        # stop all your service and unlease-app for this user

        print "%s uninstalled App"%self.req["user_id"]

        user_id    = self.req["user_id"]
        zone       = self.req["zone"]
        self.get_connection(None, zone).unlease_app([user_id, settings.APP_ID])

    def suspend_resource(self):
        # do something to stop your service

        print "App resource %s for %s of %s has been suspended" \
                %(self.req["appr_id"], self.req["service_id"],
                  self.req["user_id"])

    def resume_resource(self):
        # do something to resume your service

        print "App resource %s for %s of %s has been resumed" \
                %(self.req["appr_id"], self.req["service_id"],
                  self.req["user_id"])    

    def terminate_resource(self):
        print "Related QC resource of %s for %s of %s has been terminated" \
                %(self.req["appr_id"], self.req["service_id"],
                  self.req["user_id"])
        appr_id    = self.req["appr_id"]
        zone       = self.req["zone"]
        self.get_connection(None, zone).unlease_app([appr_id])
