import json
import re

class AmsHandleExceptions(Exception):

    def __init__(self, json, request):
        print json
        self.code = json['error']['code']
        self.msg = "While Trying the [" + request +"]:"+ json['error']['message']
        super(self.__class__, self).__init__(dict(error=self.msg,status_code=self.code))
    