import json
from base64 import b64encode, b64decode
from collections import Callable

class AmsMessage(Callable):
    def __init__(self, b64enc=True, attributes=None, data=None,
                 messageId=None, publishTime=None):
        self.attributes = attributes
        self.data = b64encode(data) if b64enc and data else data
        self.messageId = messageId
        self.publishTime = publishTime

    def __call__(self, **kwargs):
        self.__init__(b64enc=True, **kwargs)
        return self.dict()

    def set_attr(self, key, value):
        self.attributes.update({key: value})

    def set_data(self, data):
        self.data = b64encode(data)

    def dict(self):
        d = dict()
        for attr in ['attributes', 'data', 'messageId', 'publishTime']:
            v = eval('self.{0}'.format(attr))
            if v:
                d.update({attr: v})
        return d

    def get_data(self):
        return b64decode(self.data)

    def get_msgid(self):
        return self.messageId

    def json(self):
        return json.dumps(self.dict())

    def __str__(self):
        return str(self.dict())
