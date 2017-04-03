import json
import re

class AmsException(Exception):
    def __init__(self, *args, **kwargs):
        super(AmsException, self).__init__(*args, **kwargs)

class AmsServiceException(AmsException):
    def __init__(self, json, request):
        self.code = json['error']['code']
        self.msg = "While trying the [{0}]: {1}".format(request, json['error']['message'])
        super(AmsServiceException, self).__init__(dict(error=self.msg, status_code=self.code))

class AmsConnectionException(AmsException):
    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, repr(exp))
        super(AmsConnectionException, self).__init__(self.msg)

class AmsMessageException(AmsException):
    def __init__(self, msg):
        self.msg = msg
        super(AmsMessageException, self).__init__(self.msg)
