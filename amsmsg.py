import json
from base64 import b64encode

class AmsMessage(object):
    def __init__(self, attributes=dict(), data=""):
        self.attributes = attributes
        self.data = b64encode(data)

    def set_attr(self, key, value):
        self.attributes.update({key: value})

    def set_data(self, data):
        self.data = b64encode(data)

    def dict(self):
        return {'attributes': self.attributes,
                'data': self.data}

    def json(self):
        return json.dumps(self.dict())
