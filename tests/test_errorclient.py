import unittest
from httmock import urlmatch, HTTMock, response
from pymod import ArgoMessagingService
from pymod import AmsMessage
from pymod import AmsTopic
from pymod import AmsSubscription
from pymod import AmsServiceException
import json

from amsmocks import SubMocks
from amsmocks import TopicMocks


class TestErrorClient(unittest.TestCase):
    def setUp(self):
        # Initialize ams in localhost with token s3cr3t and project TEST
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t", project="TEST")
        self.submocks = SubMocks()
        self.topicmocks = TopicMocks()

    # Test create topic client request
    def testCreateTopics(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.create_topic_alreadyexist_mock):
            try:
                resp = self.ams.create_topic("topic1")
            except Exception as e:
                assert isinstance(e, AmsServiceException)
                self.assertEqual(e.status, 'ALREADY_EXIST')
                self.assertEqual(e.code, 409)



if __name__ == '__main__':
    unittest.main()
