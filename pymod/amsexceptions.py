import json
import re

strerr = ''
num_excp_expand = 0

def errmsg_from_excp(e, level=6):
    global strerr, num_excp_expand
    if isinstance(e, Exception) and getattr(e, 'args', False):
        num_excp_expand += 1
        if not errmsg_from_excp(e.args):
            return strerr
    elif isinstance(e, dict):
        for s in e.iteritems():
            errmsg_from_excp(s)
    elif isinstance(e, list):
        for s in e:
            errmsg_from_excp(s)
    elif isinstance(e, tuple):
        for s in e:
            errmsg_from_excp(s)
    elif isinstance(e, str):
        if num_excp_expand <= level:
            strerr += e + ' '

class AmsServiceException(Exception):
    def __init__(self, json, request):
        self.code = json['error']['code']
        self.msg = "While trying the [{0}: {1}".format(request, json['error']['message'])
        super(self.__class__, self).__init__(dict(error=self.msg, status_code=self.code))

class AmsConnectionException(Exception):
    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, errmsg_from_excp(exp))
        super(self.__class__, self).__init__(self.msg)
