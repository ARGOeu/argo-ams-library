import json
import re

class AmsServiceException(Exception):
    def __init__(self, json, request):
        self.code = json['error']['code']
        self.msg = "While trying the [{0}: {1}".format(request, json['error']['message'])
        super(self.__class__, self).__init__(dict(error=self.msg, status_code=self.code))

class AmsConnectionException(Exception):
    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, repr(exp))
        super(self.__class__, self).__init__(self.msg)
