import unittest
from httmock import urlmatch, HTTMock, response
from pymod import ArgoMessagingService
from pymod import AmsMessage
from pymod import AmsTopic
from pymod import AmsSubscription
from pymod import AmsServiceException, AmsException
import json

from amsmocks import ErrorMocks
from amsmocks import TopicMocks
from amsmocks import SubMocks


class TestErrorClient(unittest.TestCase):
    def setUp(self):
        # Initialize ams in localhost with token s3cr3t and project TEST
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t", project="TEST")
        self.errormocks = ErrorMocks()
        self.topicmocks = TopicMocks()
        self.submocks = SubMocks()

    # Test create topic client request
    def testCreateTopics(self):
        # Execute ams client with mocked response
        with HTTMock(self.errormocks.create_topic_alreadyexist_mock):
            try:
                resp = self.ams.create_topic("topic1")
            except Exception as e:
                assert isinstance(e, AmsServiceException)
                self.assertEqual(e.status, 'ALREADY_EXIST')
                self.assertEqual(e.code, 409)

    def testCreateSubscription(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.get_topic_mock,
                     self.errormocks.create_subscription_alreadyexist_mock):
            try:
                resp = self.ams.create_sub("subscription1", "topic1", 10)
            except Exception as e:
                assert isinstance(e, AmsServiceException)
                self.assertEqual(e.status, 'ALREADY_EXIST')
                self.assertEqual(e.code, 409)

    # Test Publish client request
    def testFailedPublish(self):
        # Mock response for POST publish to topic
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1:publish",
                  method="POST")
        def publish_mock(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1:publish"
            # Check request produced by ams client
            req_body = json.loads(request.body)
            assert req_body["messages"][0]["data"] == "Zm9vMQ=="
            assert req_body["messages"][0]["attributes"]["bar1"] == "baz1"
            return response(504, '<htmI><body><h1>504 Gateway Time-out</h1>\nThe server didn\'t respond in time.\n</body></html>\n', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(publish_mock):
            msg = AmsMessage(data='foo1', attributes={'bar1': 'baz1'})
            try:
                resp = self.ams.publish("topic1", msg)
            except Exception as e:
                assert isinstance(e, AmsServiceException)
                self.assertEqual(e.code, 504)

    # Tests for plaintext or JSON encoded backend error messages
    def testErrorMsgBackend(self):
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method='GET')
        def error_plaintxt(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1"
            return response(500, "Cannot get topic", None, None, 5, request)

        with HTTMock(error_plaintxt):
            try:
                resp = self.ams.get_topic("topic1")
            except AmsServiceException as e:
                self.assertEqual(e.msg, "While trying the [topic_get]: Cannot get topic")

        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method='GET')
        def error_json(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1"
            return response(500, json.loads('{"error": {"code": 500,\
                                              "message": "Cannot get topic",\
                                              "status": "INTERNAL_SERVER_ERROR"\
                                              }}'), None, None, 5, request)

        with HTTMock(error_json):
            try:
                resp = self.ams.get_topic("topic1")
            except AmsServiceException as e:
                self.assertEqual(e.code, 500)
                self.assertEqual(e.msg, "While trying the [topic_get]: Cannot get topic")
                self.assertEqual(e.status, "INTERNAL_SERVER_ERROR")

if __name__ == '__main__':
    unittest.main()
