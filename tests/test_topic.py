import unittest
import json

from httmock import urlmatch, HTTMock, response
from pymod import AmsMessage
from pymod import AmsServiceException
from pymod import AmsSubscription
from pymod import AmsTopic
from pymod import ArgoMessagingService

class TestTopic(unittest.TestCase):
    def setUp(self):
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                        project="TEST")
        self.msg = AmsMessage(attributes={'foo': 'bar'}, data='baz')

    def testPublish(self):
        # Mock response for PUT topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="PUT")
        def create_topic_mock(url, request):
            return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

        # Mock response for POST publish to topic
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1:publish",
                  method="POST")
        def publish_mock(url, request):
            # Check request produced by ams client
            req_body = json.loads(request.body)
            self.assertEqual(req_body["messages"][0]["data"], 'YmF6')
            self.assertEqual(req_body["messages"][0]["attributes"]["foo"], "bar")
            return '{"msgIds":["1"]}'

        # Execute ams client with mocked response
        with HTTMock(create_topic_mock, publish_mock):
            topic = self.ams.topic('topic1')
            resp = topic.publish(self.msg.dict())
            # Assert that ams client handled the json response correctly
            self.assertEqual(resp["msgIds"][0], "1")
            self.assertEqual(topic.name, 'topic1')
            self.assertEqual(topic.fullname, '/projects/TEST/topics/topic1')

    def testSubscription(self):
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

        # Execute ams client with mocked response
        with HTTMock(create_topic_mock, create_subscription_mock, get_topic_mock):
            topic = self.ams.topic('topic1')
            sub = topic.subscription('subscription1')
            # Assert that ams client handled the json response correctly
            self.assertEqual(topic.name, 'topic1')
            self.assertEqual(topic.fullname, '/projects/TEST/topics/topic1')
            assert isinstance(sub, AmsSubscription)
            self.assertEqual(sub.topic, topic)
            self.assertEqual(sub.name, 'subscription1')
            self.assertEqual(sub.fullname, '/projects/TEST/subscriptions/subscription1')

    def testIterSubscriptions(self):
        # Mock response for PUT topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="PUT")
        def create_topic_mock(url, request):
            return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

        # Mock response for GET Subscriptions request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions",
                  method="GET")
        def iter_subs_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions"
            # Return two topics in json format
            return response(200, '{"subscriptions":[{"name": "/projects/TEST/subscriptions/subscription1",\
                                  "topic": "/projects/TEST/topics/topic1","pushConfig": \
                                  {"pushEndpoint": "","retryPolicy": {}},"ackDeadlineSeconds": 10},\
                                  {"name": "/projects/TEST/subscriptions/subscription2", \
                                  "topic": "/projects/TEST/topics/topic1", \
                                  "pushConfig": {"pushEndpoint": "","retryPolicy": {}},\
                                  "ackDeadlineSeconds": 10}]}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(iter_subs_mock, create_topic_mock):
            topic = self.ams.topic('topic1')
            resp = topic.iter_subs()
            obj1 = resp.next()
            obj2 = resp.next()
            assert isinstance(obj1, AmsSubscription)
            assert isinstance(obj2, AmsSubscription)
            self.assertRaises(StopIteration, resp.next)
            self.assertEqual(obj1.name, 'subscription1')
            self.assertEqual(obj2.name, 'subscription2')

    def testDelete(self):
        # Mock response for PUT topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="PUT")
        def create_topic_mock(url, request):
            return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

        # Mock response for DELETE topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="DELETE")
        def delete_topic(url, request):
            return response(200, '{}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(delete_topic, create_topic_mock):
            topic = self.ams.topic('topic1')
            self.assertTrue(topic.delete())

if __name__ == '__main__':
    unittest.main()
