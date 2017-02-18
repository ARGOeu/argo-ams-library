import json
from base64 import b64encode, b64decode

class AmsMessage(object):
    def __init__(self, *args, **kwargs):
        self.attributes = kwargs['attributes']
        self.data = b64encode(kwargs['data'])

    def set_attr(self, key, value):
        self.attributes.update({key: value})

    def set_data(self, data):
        self.data = b64encode(data)

    def dict(self):
        return {'attributes': self.attributes,
                'data': self.data}

    def get_data(self):
        return b64decode(self.data)

    def json(self):
        return json.dumps(self.dict())
