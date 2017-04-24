import unittest
import json

from httmock import urlmatch, HTTMock, response
from pymod import AmsMessage
from pymod import AmsServiceException
from pymod import AmsSubscription
from pymod import AmsTopic
from pymod import ArgoMessagingService

class TestSubscription(unittest.TestCase):
    def setUp(self):
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                        project="TEST")
        self.msg = AmsMessage(attributes={'foo': 'bar'}, data='baz')

    def testPushConfig(self):
        # Mock response for GET topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="GET")
        def get_topic_mock(url, request):
            # Return the details of a topic in json format
            return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

        # Mock response for PUT topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="PUT")
        def create_topic_mock(url, request):
            return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

        # Mock response for PUT topic request
        @urlmatch(netloc="localhost",
                  path="/v1/projects/TEST/subscriptions/subscription1",
                  method="PUT")
        def create_subscription_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1"
            # Return two topics in json format
            return response(200,
                            '{"name": "/projects/TEST/subscriptions/subscription1",\
                            "topic":"/projects/TEST/topics/topic1",\
                            "pushConfig":{"pushEndpoint":"","retryPolicy":{}},"ackDeadlineSeconds": 10}',
                            None, None, 5, request)

        # Mock response for POST pushconfig request
        @urlmatch(netloc="localhost",
                  path="/v1/projects/TEST/subscriptions/subscription1:modifyPushConfig",
                  method="POST")
        def modify_pushconfig_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:modifyPushConfig"
            # Return two topics in json format
            return response(200,
                            '{"name": "/projects/TEST/subscriptions/subscription1",\
                            "topic":"/projects/TEST/topics/topic1",\
                            "pushConfig":{"pushEndpoint":"https://myproject.appspot.com/myhandler","retryPolicy":{"type":"linear", "period":300 }},"ackDeadlineSeconds": 10}',
                            None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(create_topic_mock, create_subscription_mock, get_topic_mock, modify_pushconfig_mock):
            topic = self.ams.topic('topic1')
            sub = topic.subscription('subscription1')
            self.assertEqual(topic.name, 'topic1')
            self.assertEqual(topic.fullname, '/projects/TEST/topics/topic1')
            assert isinstance(sub, AmsSubscription)
            self.assertEqual(sub.name, 'subscription1')
            self.assertEqual(sub.fullname, '/projects/TEST/subscriptions/subscription1')
            self.assertEqual(sub.push_endpoint, '')
            self.assertEqual(sub.retry_policy_type, '')
            self.assertEqual(sub.retry_policy_period, '')
            self.assertEqual(sub.ackdeadline, 10)
            resp = sub.pushconfig(push_endpoint='https://myproject.appspot.com/myhandler1')
            self.assertEqual(resp['pushConfig']['pushEndpoint'], "https://myproject.appspot.com/myhandler")
            self.assertEqual(resp['pushConfig']['retryPolicy']['type'], "linear")
            self.assertEqual(resp['pushConfig']['retryPolicy']['period'], 300)


if __name__ == '__main__':
    unittest.main()
