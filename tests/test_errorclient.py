import json
import mock
import sys
import unittest
import requests

from httmock import urlmatch, HTTMock, response
from pymod import ArgoMessagingService
from pymod import AmsMessage
from pymod import AmsTopic
from pymod import AmsSubscription
from pymod import (AmsServiceException, AmsConnectionException,
                   AmsTimeoutException, AmsBalancerException, AmsException)

from .amsmocks import ErrorMocks
from .amsmocks import TopicMocks
from .amsmocks import SubMocks


class TestErrorClient(unittest.TestCase):
    def setUp(self):
        # Initialize ams in localhost with token s3cr3t and project TEST
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t", project="TEST")
        self.errormocks = ErrorMocks()
        self.topicmocks = TopicMocks()
        self.submocks = SubMocks()

        # set defaults for testing of retries
        retry = 0
        retrysleep = 0.1
        retrybackoff = None
        if sys.version_info < (3, ):
            self.ams._retry_make_request.im_func.func_defaults = (None, None, retry, retrysleep, retrybackoff)
        else:
            self.ams._retry_make_request.__func__.__defaults__ = (None, None, retry, retrysleep, retrybackoff)

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

    # Test delete topic client request
    def testDeleteTopics(self):
        # Execute ams client with mocked response
        with HTTMock(self.errormocks.delete_topic_notfound_mock):
            try:
                resp = self.ams.delete_topic("topic1")
            except Exception as e:
                assert isinstance(e, AmsServiceException)
                self.assertEqual(e.status, 'NOT_FOUND')
                self.assertEqual(e.code, 404)

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
                assert isinstance(e, AmsTimeoutException)
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
                if sys.version_info < (3, 6 ):
                    response_string = "Cannot get topic"
                else:
                    response_string = "b'Cannot get topic'"
                self.assertEqual(e.msg, "While trying the [topic_get]: " + response_string)

        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method='GET')
        def error_json(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1"
            return response(500, '{"error": {"code": 500,\
                                              "message": "Cannot get topic",\
                                              "status": "INTERNAL_SERVER_ERROR"\
                                            }}', None, None, 5, request)

        with HTTMock(error_json):
            try:
                resp = self.ams.get_topic("topic1")
            except AmsServiceException as e:
                self.assertEqual(e.code, 500)
                self.assertEqual(e.msg, "While trying the [topic_get]: Cannot get topic")
                self.assertEqual(e.status, "INTERNAL_SERVER_ERROR")

    def testUnauthorized(self):
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method='GET')
        def error_unauth(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1"
            return response(401, '{"error": {"code": 401, \
                                             "message": "Unauthorized", \
                                             "status": "UNAUTHORIZED"}}')
        with HTTMock(error_unauth):
            try:
                resp = self.ams.get_topic("topic1")
            except AmsServiceException as e:
                self.assertEqual(e.code, 401)
                self.assertEqual(e.msg, 'While trying the [topic_get]: Unauthorized')
                self.assertEqual(e.status, 'UNAUTHORIZED')

    def testModifyOffset(self):
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1:modifyOffset",
                  method='POST')
        def error_modoffset(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:modifyOffset"
            return response(400, '{"error": {"message": "Offset out of bounds", \
                                             "code": 400, \
                                             "status": "INVALID_ARGUMENT"}}')
        with HTTMock(error_modoffset):
            try:
                resp = self.ams.modifyoffset_sub("subscription1", 1)
            except AmsServiceException as e:
                self.assertEqual(e.code, 400)
                self.assertEqual(e.status, 'INVALID_ARGUMENT')
                self.assertEqual(e.msg, "While trying the [sub_mod_offset]: Offset out of bounds")

    @mock.patch('pymod.ams.requests.get')
    def testRetryConnectionProblems(self, mock_requests_get):
        mock_requests_get.side_effect = [requests.exceptions.ReadTimeout,
                                         requests.exceptions.ConnectionError,
                                         requests.exceptions.ConnectionError,
                                         requests.exceptions.ConnectionError]
        retry = 3
        retrysleep = 0.1
        if sys.version_info < (3, ):
            self.ams._retry_make_request.im_func.func_defaults = (None, None, retry, retrysleep, None)
        else:
            self.ams._retry_make_request.__func__.__defaults__ = (None, None, retry, retrysleep, None)
        self.assertRaises(AmsConnectionException, self.ams.list_topics)
        self.assertEqual(mock_requests_get.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.get')
    def testBackoffRetryConnectionProblems(self, mock_requests_get):
        mock_requests_get.side_effect = [requests.exceptions.ConnectionError,
                                         requests.exceptions.ConnectionError,
                                         requests.exceptions.ConnectionError,
                                         requests.exceptions.ConnectionError]
        retry = 3
        retrysleep = 0.1
        retrybackoff = 0.1
        if sys.version_info < (3, ):
            self.ams._retry_make_request.im_func.func_defaults = (None, None, retry, retrysleep, retrybackoff)
        else:
            self.ams._retry_make_request.__func__.__defaults__ = (None, None, retry, retrysleep, retrybackoff)
        self.assertRaises(AmsConnectionException, self.ams.list_topics)
        self.assertEqual(mock_requests_get.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.post')
    def testRetryAmsBalancerTimeout408(self, mock_requests_post):
        retry = 4
        retrysleep = 0.2
        errmsg = "<html><body><h1>408 Request Time-out</h1>\nYour browser didn't send a complete request in time.\n</body></html>\n"
        mock_response = mock.create_autospec(requests.Response)
        mock_response.status_code = 408
        mock_response.content = errmsg
        mock_requests_post.return_value = mock_response
        try:
            self.ams.pull_sub('subscription1', retry=retry, retrysleep=retrysleep)
        except Exception as e:
            assert isinstance(e, AmsTimeoutException)
            self.assertEqual(e.code, 408)
            self.assertEqual(e.msg, 'While trying the [sub_pull]: ' + errmsg)
        self.assertEqual(mock_requests_post.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.post')
    def testRetryAmsBalancer502(self, mock_requests_post):
        retry = 4
        retrysleep = 0.2
        errmsg = "<html><body><h1>502 Bad Gateway</h1>\nThe server returned an invalid or incomplete response.\n</body></html>\n"
        mock_response = mock.create_autospec(requests.Response)
        mock_response.status_code = 502
        mock_response.content = errmsg
        mock_requests_post.return_value = mock_response
        try:
            self.ams.pull_sub('subscription1', retry=retry, retrysleep=retrysleep)
        except Exception as e:
            assert isinstance(e, AmsBalancerException)
            self.assertEqual(e.code, 502)
            self.assertEqual(e.msg, 'While trying the [sub_pull]: ' + errmsg)
        self.assertEqual(mock_requests_post.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.post')
    def testRetryAmsBalancer503(self, mock_requests_post):
        retry = 4
        retrysleep = 0.2
        errmsg = "<html><body><h1>503 Service Unavailable</h1>\nNo server is available to handle this request.\n</body></html>\n"
        mock_response = mock.create_autospec(requests.Response)
        mock_response.status_code = 503
        mock_response.content = errmsg
        mock_requests_post.return_value = mock_response
        try:
            self.ams.pull_sub('subscription1', retry=retry, retrysleep=retrysleep)
        except Exception as e:
            assert isinstance(e, AmsBalancerException)
            self.assertEqual(e.code, 503)
            self.assertEqual(e.msg, 'While trying the [sub_pull]: ' + errmsg)
        self.assertEqual(mock_requests_post.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.post')
    def testRetryAmsBalancerTimeout504(self, mock_requests_post):
        retry = 4
        retrysleep = 0.2
        errmsg = "<html><body><h1>504 Gateway Time-out</h1>\nThe server didn't respond in time.\n</body></html>\n"
        mock_response = mock.create_autospec(requests.Response)
        mock_response.status_code = 504
        mock_response.content = errmsg
        mock_requests_post.return_value = mock_response
        try:
            self.ams.pull_sub('subscription1', retry=retry, retrysleep=retrysleep)
        except Exception as e:
            assert isinstance(e, AmsTimeoutException)
            self.assertEqual(e.code, 504)
            self.assertEqual(e.msg, 'While trying the [sub_pull]: ' + errmsg)
        self.assertEqual(mock_requests_post.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.get')
    def testRetryAckDeadlineAmsTimeout(self, mock_requests_get):
        mock_response = mock.create_autospec(requests.Response)
        mock_response.status_code = 408
        mock_response.content = '{"error": {"code": 408, \
                                            "message": "Ams Timeout", \
                                            "status": "TIMEOUT"}}'
        mock_requests_get.return_value = mock_response
        retry = 3
        retrysleep = 0.1
        if sys.version_info < (3, ):
            self.ams._retry_make_request.im_func.__defaults__ = (None, None, retry, retrysleep, None)
        else:
            self.ams._retry_make_request.__func__.__defaults__ = (None, None, retry, retrysleep, None)
        self.assertRaises(AmsTimeoutException, self.ams.list_topics)
        self.assertEqual(mock_requests_get.call_count, retry + 1)

    @mock.patch('pymod.ams.requests.post')
    def testPullAckSub(self, mock_requests_post):
        mock_pull_response = mock.create_autospec(requests.Response)
        mock_pull_response.status_code = 200
        mock_pull_response.content = '{"receivedMessages":[{"ackId":"projects/TEST/subscriptions/subscription1:1221",\
                    "message":{"messageId":"1221","attributes":{"foo":"bar"},"data":"YmFzZTY0ZW5jb2RlZA==",\
                    "publishTime":"2016-02-24T11:55:09.786127994Z"}}]}'

        mock_failedack_response = mock.create_autospec(requests.Response)
        mock_failedack_response.status_code = 408
        mock_failedack_response.content = '{"error": {"code": 408,\
                                                     "message": "Ams Timeout",\
                                                     "status": "TIMEOUT"}}'

        mock_successack_response = mock.create_autospec(requests.Response)
        mock_successack_response.status_code = 200
        mock_successack_response.content = '200 OK'

        mock_requests_post.side_effect = [mock_pull_response,
                                          mock_failedack_response,
                                          mock_pull_response,
                                          mock_successack_response]

        resp_pullack = self.ams.pullack_sub("subscription1", 1)
        assert isinstance(resp_pullack, list)
        assert isinstance(resp_pullack[0], AmsMessage)
        if sys.version_info < (3, ):
            self.assertEqual(resp_pullack[0].get_data(), "base64encoded")
        else:
            self.assertEqual(resp_pullack[0].get_data(), b"base64encoded")
        self.assertEqual(resp_pullack[0].get_msgid(), "1221")


if __name__ == '__main__':
    unittest.main()
