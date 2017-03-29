import unittest

from pymod import AmsMessage
from pymod import AmsMessageException

class TestMessage(unittest.TestCase):

    def setUp(self):
        m = AmsMessage()
        self.message_callable = m(attributes={'foo': 'bar'}, data='baz')
        self.message_callable_nodata = m(attributes={'foo': 'bar'})
        self.message_send = AmsMessage(attributes={'foo': 'bar'}, data='baz')
        self.message_send_no_data = AmsMessage(attributes={'foo': 'bar'})

        self.message_recv = AmsMessage(b64enc=False, attributes={'foo': 'bar'},
                                       data='YmF6', messageId='1',
                                       publishTime='2017-03-15T17:11:34.035345612Z')
        self.message_recv_faulty = AmsMessage(b64enc=False, attributes={'foo': 'bar'},
                                              data='123456789thiswillfail',
                                              messageId='1',
                                              publishTime='2017-03-15T17:11:34.035345612Z')

    def test_MsgReadyToSend(self):
        self.assertEqual(self.message_send.dict(), {'attributes': {'foo': 'bar'},
                                                    'data': 'YmF6'})
        self.assertEqual(self.message_callable, {'attributes': {'foo': 'bar'},
                                                 'data': 'YmF6'})
        self.message_send.set_data('baz')
        self.assertEqual(self.message_send.get_data(), 'baz')

    def test_MsgReadyToRecv(self):
        self.assertEqual(self.message_recv.get_data(), 'baz')
        self.assertEqual(self.message_recv.get_msgid(), '1')
        self.assertEqual(self.message_recv.get_publishtime(),
                         '2017-03-15T17:11:34.035345612Z')
        self.assertEqual(self.message_recv.get_attr(), {'foo': 'bar'})

    def test_MsgFaulty(self):
        self.assertRaises(AmsMessageException, self.message_recv_faulty.get_data)
        self.assertRaises(AmsMessageException, self.message_send_no_data.get_data)

if __name__ == '__main__':
    unittest.main()
