import unittest
import json

from httmock import urlmatch, HTTMock, response
from pymod import AmsMessage
from pymod import AmsServiceException
from pymod import AmsSubscription
from pymod import AmsTopic
from pymod import ArgoMessagingService


class SubMocks(object):
    get_topic_urlmatch = dict(netloc="localhost",
                              path="/v1/projects/TEST/topics/topic1",
                              method='GET')

    create_topic_urlmatch = dict(netloc="localhost",
                                 path="/v1/projects/TEST/topics/topic1",
                                 method='PUT')

    get_sub_urlmatch = dict(netloc="localhost",
                            path="/v1/projects/TEST/subscriptions/subscription1",
                            method="GET")

    create_subscription_urlmatch = dict(netloc="localhost",
                                        path="/v1/projects/TEST/subscriptions/subscription1",
                                        method="PUT")

    @urlmatch(**get_topic_urlmatch)
    def get_topic_mock(self, url, request):
        # Return the details of a topic in json format
        return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

    # Mock response for PUT topic request
    @urlmatch(**create_topic_urlmatch)
    def create_topic_mock(self, url, request):
        return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

    # Mock response for GET subscription request
    @urlmatch(**get_sub_urlmatch)
    def get_sub_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1"
        # Return the details of a subscription in json format
        return response(200, '{"name":"/projects/TEST/subscriptions/subscription1",\
                        "topic":"/projects/TEST/topics/topic1",\
                        "pushConfig": {"pushEndpoint": "","retryPolicy": {}},\
                        "ackDeadlineSeconds": 10}', None, None, 5, request)

    # Mock response for PUT topic request
    @urlmatch(create_topic_urlmatch)
    def create_subscription_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1"
        # Return two topics in json format
        return response(200,
                        '{"name": "/projects/TEST/subscriptions/subscription1",\
                        "topic":"/projects/TEST/topics/topic1",\
                        "pushConfig":{"pushEndpoint":"","retryPolicy":{}},"ackDeadlineSeconds": 10}',
                        None, None, 5, request)

class TestSubscription(unittest.TestCase):
    def setUp(self):
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                        project="TEST")
        self.msg = AmsMessage(attributes={'foo': 'bar'}, data='baz')
        self.submocks = SubMocks()

    def testPushConfig(self):
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
        with HTTMock(self.submocks.create_topic_mock,
                     self.submocks.create_subscription_mock,
                     self.submocks.get_topic_mock, modify_pushconfig_mock,
                     self.submocks.get_sub_mock):
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

    def testPull(self):
        # Mock response for POST pull from subscription
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1:pull",
                  method="POST")
        def pull_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:pull"

            # Check request produced by ams client
            req_body = json.loads(request.body)
            assert req_body["maxMessages"] == "1"
            return '{"receivedMessages":[{"ackId":"projects/TEST/subscriptions/subscription1:1221",\
                    "message":{"messageId":"1221","attributes":{"foo":"bar"},"data":"YmFzZTY0ZW5jb2RlZA==",\
                    "publishTime":"2016-02-24T11:55:09.786127994Z"}}]}'

        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1:acknowledge",
                  method="POST")
        def ack_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:acknowledge"
            # Error: library returns json in the form {"ackIds": 1221}
            assert request.body == '{"ackIds": ["1221"]}'
            # Check request produced by ams client
            return '{}'

        # Execute ams client with mocked response
        with HTTMock(pull_mock, ack_mock, self.submocks.get_sub_mock,
                     self.submocks.create_topic_mock,
                     self.submocks.get_topic_mock,
                     self.submocks.create_subscription_mock):
            topic = self.ams.topic('topic1')
            sub = topic.subscription('subscription1')
            assert isinstance(sub, AmsSubscription)
            self.assertEqual(topic.name, 'topic1')
            self.assertEqual(topic.fullname, '/projects/TEST/topics/topic1')
            self.assertEqual(sub.name, 'subscription1')
            self.assertEqual(sub.fullname, '/projects/TEST/subscriptions/subscription1')

            resp_pull = sub.pull(1)
            ack_id, msg = resp_pull[0]

            self.assertEqual(ack_id, "projects/TEST/subscriptions/subscription1:1221")
            self.assertEqual(msg.get_data(), "base64encoded")
            self.assertEqual(msg.get_msgid(), "1221")
            resp_ack = sub.ack(["1221"])
            self.assertEqual(resp_ack, True)

    def testDelete(self):
        # Mock response for DELETE topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1",
                  method="DELETE")
        def delete_subscription(url, request):
            return response(200, '{}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(delete_subscription, self.submocks.create_topic_mock,
                     self.submocks.create_subscription_mock,
                     self.submocks.get_topic_mock, self.submocks.get_sub_mock):
            topic = self.ams.topic('topic1')
            sub = topic.subscription('subscription1')
            self.assertTrue(sub.delete())

    def testAcl(self):
        # Mock response for GET topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1:modifyAcl",
                  method="POST")
        def modifyacl_sub_mock(url, request):
            self.assertEqual(url.path, "/v1/projects/TEST/subscriptions/subscription1:modifyAcl")
            self.assertEqual(request.body, '{"authorized_users": ["user1", "user2"]}')
            # Return the details of a topic in json format
            return response(200, '{}', None, None, 5, request)

        # Mock response for GET topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1:acl",
                  method="GET")
        def getacl_sub_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:acl"
            # Return the details of a topic in json format
            return response(200, '{"authorized_users": ["user1", "user2"]}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(self.submocks.create_topic_mock,
                     self.submocks.get_topic_mock, getacl_sub_mock,
                     self.submocks.get_sub_mock, modifyacl_sub_mock):
            topic = self.ams.topic('topic1')
            sub = topic.subscription('subscription1')
            ret = sub.acl(['user1', 'user2'])
            self.assertTrue(ret)
            resp_users = sub.acl()
            self.assertEqual(resp_users['authorized_users'], ['user1', 'user2'])


if __name__ == '__main__':
    unittest.main()
