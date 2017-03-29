import json
import inspect
from base64 import b64encode, b64decode
from collections import Callable
from amsexceptions import AmsMessageException

class AmsMessage(Callable):
    def __init__(self, b64enc=True, attributes=None, data=None,
                 messageId=None, publishTime=None):
        self._attributes = attributes
        self._messageId = messageId
        self._publishTime = publishTime
        self.set_data(data, b64enc)

    def __call__(self, **kwargs):
        self.__init__(b64enc=True, **kwargs)

        return self.dict()

    def _has_data(self):
        if not getattr(self, '_data', False):
            raise AmsMessageException('No message data defined')

        return True

    def set_attr(self, key, value):
        self._attributes.update({key: value})

    def set_data(self, data, b64enc=True):
        if b64enc and data:
            self._data = b64encode(data)
        elif data:
            self._data = data

    def dict(self):
        if self._has_data():
            d = dict()
            for attr in ['attributes', 'data', 'messageId', 'publishTime']:
                v = eval('self._{0}'.format(attr))
                if v:
                    d.update({attr: v})
            return d

    def get_data(self):
        if self._has_data():
            try:
                return b64decode(self._data)
            except Exception as e:
                raise AmsMessageException('b64decode() {0}'.format(str(e)))

    def get_msgid(self):
        return self._messageId

    def get_publishtime(self):
        return self._publishTime

    def get_attr(self):
        return self._attributes

    def json(self):
        return json.dumps(self.dict())

    def __str__(self):
        return str(self.dict())
