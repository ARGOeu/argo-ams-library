import json

class AmsException(Exception):
    """
       Base exception class for all Argo Messaging service related errors
    """
    def __init__(self, *args, **kwargs):
        super(AmsException, self).__init__(*args, **kwargs)


class AmsServiceException(AmsException):
    """
       Exception for Argo Messaging Service API errors
    """
    def __init__(self, json, request):
        errord = dict()

        self.msg = "While trying the [{0}]: {1}".format(request, json['error']['message'])
        errord.update(error=self.msg)

        if json['error'].get('code'):
            self.code = json['error']['code']
            errord.update(status_code=self.code)

        if json['error'].get('status'):
            self.status = json['error']['status']
            errord.update(status=self.status)

        super(AmsServiceException, self).__init__(errord)


class AmsBalancerException(AmsException):
    """
       Exception for HAProxy Argo Messaging Service errors
    """
    def __init__(self, json, request):
        errord = dict()

        self.msg = "While trying the [{0}]: {1}".format(request, json['error']['message'])
        errord.update(error=self.msg)

        if json['error'].get('code'):
            self.code = json['error']['code']
            errord.update(status_code=self.code)

        if json['error'].get('status'):
            self.status = json['error']['status']
            errord.update(status=self.status)

        super(AmsException, self).__init__(errord)


class AmsTimeoutException(AmsServiceException):
    """
       Exception for timeout returned by the Argo Messaging Service if message
       was not acknownledged in desired time frame (ackDeadlineSeconds)
    """
    def __init__(self, json, request):
        super(AmsServiceException, self).__init__(json, request)


class AmsConnectionException(AmsException):
    """
       Exception for connection related problems catched from requests library
    """
    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, repr(exp))
        super(AmsConnectionException, self).__init__(self.msg)


class AmsMessageException(AmsException):
    """
       Exception that indicate problems with constructing message
    """
    def __init__(self, msg):
        self.msg = msg
        super(AmsMessageException, self).__init__(self.msg)
