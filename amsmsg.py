import json
from base64 import b64encode, b64decode

class AmsMessage(object):
    def __init__(self, attributes='', data='',
                 messageId='', publishTime=''):
        self.attributes = attributes
        self.data = data
        self.messageId = messageId
        self.publishTime = publishTime

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

    def json(self):
        return json.dumps(self.dict())
