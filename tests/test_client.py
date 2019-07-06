import json
import sys
import unittest

from httmock import urlmatch, HTTMock, response
from pymod import ArgoMessagingService
from pymod import AmsMessage
from pymod import AmsTopic
from pymod import AmsSubscription

from .amsmocks import SubMocks
from .amsmocks import TopicMocks


class TestClient(unittest.TestCase):
    def setUp(self):
        # Initialize ams in localhost with token s3cr3t and project TEST
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t", project="TEST")
        self.submocks = SubMocks()
        self.topicmocks = TopicMocks()

    # Test create topic client request
    def testCreateTopics(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.create_topic_mock):
            resp = self.ams.create_topic("topic1")
            resp_obj = self.ams.create_topic("topic1", retobj=True)
            # Assert that ams client handled the json response correctly
            name = resp["name"]
            assert name == "/projects/TEST/topics/topic1"
            assert isinstance(resp_obj, AmsTopic)
            self.assertEqual(resp_obj.name, "topic1")

    # Test Pull client request
    def testPull(self):
        # Mock response for POST pull from subscription
        @urlmatch(netloc="localhost",
                  path="/v1/projects/TEST/subscriptions/subscription1:pull",
                  method="POST")
        def pull_mock(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:pull"

            # Check request produced by ams client
            req_body = json.loads(request.body)
            assert req_body["maxMessages"] == "1"
            return '{"receivedMessages":[{"ackId":"projects/TEST/subscriptions/subscription1:1221",\
                    "message":{"messageId":"1221","attributes":{"foo":"bar"},"data":"YmFzZTY0ZW5jb2RlZA==",\
                    "publishTime":"2016-02-24T11:55:09.786127994Z"}}]}'

        # Execute ams client with mocked response
        with HTTMock(pull_mock, self.submocks.ack_mock, self.submocks.get_sub_mock):

            # msg = AmsMessage(data='foo1', attributes={'bar1': 'baz1'}).dict()
            resp_pull = self.ams.pull_sub("subscription1", 1)
            ack_id, msg = resp_pull[0]
            assert ack_id == "projects/TEST/subscriptions/subscription1:1221"
            assert msg.get_data() == "base64encoded"
            assert msg.get_msgid() == "1221"
            # Note: Maybe ack_sub should return a boolean
            resp_ack = self.ams.ack_sub("subscription1", ["1221"])
            assert resp_ack == True

    # Test Create subscription client request
    def testCreateSubscription(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.get_topic_mock,
                     self.submocks.create_subscription_mock):
            resp = self.ams.create_sub("subscription1", "topic1", 10)

            # Assert that ams client handled the json response correctly
            name = resp["name"]
            assert name == "/projects/TEST/subscriptions/subscription1"

    # Test the Modify offset client request
    def testModifyOffset(self):
        # Execute ams client with mocked response
        with HTTMock(self.submocks.modifyoffset_sub_mock):
            resp = self.ams.modifyoffset_sub("subscription1", 79)
            self.assertEquals(resp, {})

    # Test the Get offsets client request
    def testGetOffsets(self):
        # Execute ams client with mocked response
        with HTTMock(self.submocks.getoffsets_sub_mock):
            # should return a dict with all the offsets
            resp_all = self.ams.getoffsets_sub("subscription1")
            resp_dict_all = {
                "max": 79,
                "min": 0,
                "current": 78
            }
            # should return the max offset
            resp_max = self.ams.getoffsets_sub("subscription1", "max")
            # should return the current offset
            resp_current = self.ams.getoffsets_sub("subscription1", "current")
            # should return the min offset
            resp_min = self.ams.getoffsets_sub("subscription1", "min")

            self.assertEquals(resp_all, resp_dict_all)
            self.assertEquals(resp_max, 79)
            self.assertEquals(resp_current, 78)
            self.assertEquals(resp_min, 0)

    # Test List topics client request
    def testListTopics(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.list_topics_mock):
            resp = self.ams.list_topics()
            # Assert that ams client handled the json response correctly
            topics = resp["topics"]
            topic_objs = list(self.ams.topics.values())
            assert len(topics) == 2
            assert topics[0]["name"] == "/projects/TEST/topics/topic1"
            assert topics[1]["name"] == "/projects/TEST/topics/topic2"
            assert isinstance(topic_objs[0], AmsTopic)
            assert isinstance(topic_objs[1], AmsTopic)
            self.assertEqual(topic_objs[0].fullname, "/projects/TEST/topics/topic1")
            self.assertEqual(topic_objs[1].fullname, "/projects/TEST/topics/topic2")

    # Test Iteration over AmsTopic objects
    def testIterTopics(self):
        # Mock response for GET topics request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics",
                  method="GET")
        def iter_topics_mock(url, request):
            assert url.path == "/v1/projects/TEST/topics"
            # Return two topics in json format
            return response(200, '{"topics":[{"name":"/projects/TEST/topics/topic1"},\
                                  {"name":"/projects/TEST/topics/topic2"}]}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(iter_topics_mock):
            resp = self.ams.iter_topics()
            # Assert that ams client handled the json response correctly
            obj1 = next(resp)
            obj2 = next(resp)
            assert isinstance(obj1, AmsTopic)
            assert isinstance(obj2, AmsTopic)
            if sys.version_info < (3, ):
                self.assertRaises(StopIteration, resp.next)
            else:
                self.assertRaises(StopIteration, resp.__next__)
            self.assertEqual(obj1.name, 'topic1')
            self.assertEqual(obj2.name, 'topic2')

    # Test Get a subscription ACL client request
    def testGetAclSubscription(self):
        # Execute ams client with mocked response
        with HTTMock(self.submocks.getacl_subscription_mock, self.submocks.get_sub_mock):
            resp = self.ams.getacl_sub("subscription1")
            users = resp['authorized_users']
            self.assertEqual(users, [])

    # Test Modify a topic ACL client request
    def testModifyAclSubscription(self):
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions/subscription1:acl",
                  method="GET")
        def getacl_subscription_mock_filled(url, request):
            assert url.path == "/v1/projects/TEST/subscriptions/subscription1:acl"
            # Return the details of a topic in json format
            return response(200, '{"authorized_users": ["user1", "user2"]}', None, None, 5, request)


        # Execute ams client with mocked response
        with HTTMock(self.submocks.modifyacl_subscription_mock,
                     getacl_subscription_mock_filled,
                     self.submocks.get_sub_mock):
            resp = self.ams.modifyacl_sub("subscription1", ["user1", "user2"])
            self.assertTrue(resp)
            resp_users = self.ams.getacl_sub("subscription1")
            users = resp_users['authorized_users']
            self.assertEqual(users, ["user1", "user2"])

    # Test Get a topic ACL client request
    def testGetAclTopic(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.getacl_topic_mock,
                     self.topicmocks.get_topic_mock):
            resp = self.ams.getacl_topic("topic1")
            users = resp['authorized_users']
            self.assertEqual(users, [])

    # Test Modify a topic ACL client request
    def testModifyAclTopic(self):
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1:acl",
                  method="GET")
        def getacl_topic_mock_filled(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1:acl"
            # Return the details of a topic in json format
            return response(200, '{"authorized_users": ["user1", "user2"]}', None, None, 5, request)

        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.modifyacl_topic_mock,
                     getacl_topic_mock_filled, self.topicmocks.get_topic_mock):
            resp = self.ams.modifyacl_topic("topic1", ["user1", "user2"])
            self.assertTrue(resp)
            resp_users = self.ams.getacl_topic("topic1")
            users = resp_users['authorized_users']
            self.assertEqual(users, ["user1", "user2"])

    # Test Get a topic client request
    def testGetTopic(self):
        # Execute ams client with mocked response
        with HTTMock(self.topicmocks.get_topic_mock):
            resp = self.ams.get_topic("topic1")
            resp_obj = self.ams.get_topic("topic1", retobj=True)
            # Assert that ams client handled the json response correctly
            name = resp["name"]
            assert(name == "/projects/TEST/topics/topic1")
            assert isinstance(resp_obj, AmsTopic)
            self.assertEqual(resp_obj.name, 'topic1')

    # Test Publish client request
    def testPublish(self):
        # Mock response for POST publish to topic
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1:publish",
                  method="POST")
        def publish_mock(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1:publish"
            # Check request produced by ams client
            req_body = json.loads(request.body)
            assert(req_body["messages"][0]["data"] == "Zm9vMQ==")
            assert (req_body["messages"][0]["attributes"]["bar1"] == "baz1")

            return '{"msgIds":["1"]}'

        # Execute ams client with mocked response
        with HTTMock(publish_mock):
            msg = AmsMessage(data='foo1', attributes={'bar1': 'baz1'}).dict()
            msg_bulk = [AmsMessage(data='foo1', attributes={'bar1': 'baz1'}), AmsMessage(data='foo2', attributes={'bar2': 'baz2'})]
            resp = self.ams.publish("topic1", msg)
            assert resp["msgIds"][0] == "1"
            resp_bulk = self.ams.publish("topic1", msg_bulk)
            assert resp["msgIds"][0] == "1"

        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1:publish",
                  method="POST")
        def publish_bulk_mock(url, request):
            assert url.path == "/v1/projects/TEST/topics/topic1:publish"
            # Check request produced by ams client
            req_body = json.loads(request.body)
            self.assertEqual(req_body["messages"][0]["data"], "Zm9vMQ==")
            self.assertEqual(req_body["messages"][0]["attributes"]["bar1"], "baz1")
            self.assertEqual(req_body["messages"][1]["data"], "Zm9vMg==")
            self.assertEqual(req_body["messages"][1]["attributes"]["bar2"], "baz2")

            return '{"msgIds":["1", "2"]}'

        with HTTMock(publish_bulk_mock):
            msg_bulk = [AmsMessage(data='foo1', attributes={'bar1': 'baz1'}), AmsMessage(data='foo2', attributes={'bar2': 'baz2'})]
            resp_bulk = self.ams.publish("topic1", msg_bulk)
            self.assertEqual(len(resp_bulk["msgIds"]), 2)
            self.assertEqual(resp_bulk["msgIds"][0], "1")
            self.assertEqual(resp_bulk["msgIds"][1], "2")

    # Test List Subscriptions client request
    def testListSubscriptions(self):
        # Mock response for GET Subscriptions request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/subscriptions",
                  method="GET")
        def list_subs_mock(url, request):
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
        with HTTMock(list_subs_mock):
            resp = self.ams.list_subs()
            subscriptions = resp["subscriptions"]
            subscription_objs = list(self.ams.subs.values())
            topic_objs = list(self.ams.topics.values())
            # Assert that ams client handled the json response correctly
            assert len(subscriptions) == 2
            assert subscriptions[0]["name"] == "/projects/TEST/subscriptions/subscription1"
            assert subscriptions[1]["name"] == "/projects/TEST/subscriptions/subscription2"
            assert isinstance(subscription_objs[0], AmsSubscription)
            assert isinstance(subscription_objs[1], AmsSubscription)
            self.assertEqual(subscription_objs[0].fullname, "/projects/TEST/subscriptions/subscription1")
            self.assertEqual(subscription_objs[1].fullname, "/projects/TEST/subscriptions/subscription2")
            assert isinstance(topic_objs[0], AmsTopic)
            self.assertEqual(topic_objs[0].fullname, "/projects/TEST/topics/topic1")

    # Test Iteration over AmsSubscription objects
    def testIterSubscriptions(self):
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
        with HTTMock(iter_subs_mock):
            resp = self.ams.iter_subs()
            obj1 = next(resp)
            obj2 = next(resp)
            assert isinstance(obj1, AmsSubscription)
            assert isinstance(obj2, AmsSubscription)
            if sys.version_info < (3, ):
                self.assertRaises(StopIteration, resp.next)
            else:
                self.assertRaises(StopIteration, resp.__next__)
            self.assertEqual(obj1.name, 'subscription1')
            self.assertEqual(obj2.name, 'subscription2')

    # Test Get a subscriptions client request
    def testGetSubscription(self):
        # Execute ams client with mocked response
        with HTTMock(self.submocks.get_sub_mock):
            resp = self.ams.get_sub("subscription1")
            resp_obj = self.ams.get_sub("subscription1", retobj=True)
            # Assert that ams client handled the json response correctly
            name = resp["name"]
            assert name == "/projects/TEST/subscriptions/subscription1"
            assert isinstance(resp_obj, AmsSubscription)
            self.assertEqual(resp_obj.name, 'subscription1')

    # Test has topic client
    def testHasTopic(self):
        with HTTMock(self.topicmocks.get_topic_mock):
            self.assertTrue(self.ams.has_topic('topic1'))

    # Test has subscription client
    def testHasSub(self):
        with HTTMock(self.submocks.get_sub_mock):
            self.assertTrue(self.ams.has_sub('subscription1'))


if __name__ == '__main__':
    unittest.main()
