import unittest
from httmock import urlmatch, HTTMock, all_requests,response
from pymod import ArgoMessagingService
from pymod import AmsMessage
import requests

def example_401_response(url, response):
    r = requests.Response()
    print r
    r.status_code = 401
    r._content = b'Unauthorized'
    return r

class TestClient(unittest.TestCase):


    def setUp(self):
        # Initialize ams in localhost with token s3cr3t and project TEST
        self.ams = ArgoMessagingService(endpoint="localhost", token="s3cr3t",
                                   project="TEST")

    # Test create topic client request
    def testCreateTopics(self):
        # Mock response for PUT topic reqeuest
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics",
                  method="PUT")
        def create_topic_mock(url, request):
            # Return two topics in json format
            return response(200,'{"name":"/v1/projects/TEST/topics/topic1"}',None,None,5,request)
        # Execute ams client with mocked response
        with HTTMock(create_topic_mock):
            resp= self.ams.create_topic("project1")
            # Assert that ams client handled the json response correctly
            name = resp["name"]
            assert(name == "/v1/projects/TEST/topics/topic1")

    # Test List topics client request
    def testListTopics(self):
        # Mock response for GET topics reqeuest
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics",
                  method="GET")

        def list_topics_mock(url, request):
            # Return two topics in json format
            return response(200,'{"topics":[{"name":"/v1/projects/TEST/topic1"},{"name":"/v1/projects/TEST/topic2"}]}',None,None,5,request)

        # Execute ams client with mocked response
        with HTTMock(list_topics_mock):
            resp= self.ams.list_topics()
            # Assert that ams client handled the json response correctly
            topics = resp["topics"]
            assert(len(topics)==2)
            assert(topics[0]["name"] == "/v1/projects/TEST/topic1")
            assert(topics[1]["name"] == "/v1/projects/TEST/topic2")

    
    # Test Get a topic client request
    def testGetTopic(self):
        # Mock response for GET topic request
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1",
                  method="GET")

        def get_topic_mock(url, request):
            # Return the details of a topic in json format
            return response(200,'{"name":"/v1/projects/TEST/topics/topic1"}',None,None,5,request)

        # Execute ams client with mocked response
        with HTTMock(get_topic_mock):
            resp= self.ams.get_topic("topic1")
            # Assert that ams client handled the json response correctly
            name = resp["name"]
            assert(name == "/v1/projects/TEST/topics/topic1")


    # Test Publish client request
    def testPublish(self):
        # Mock response for POST publish to topic
        @urlmatch(netloc="localhost", path="/v1/projects/TEST/topics/topic1:publish",
                  method="POST")
        def publish_mock(url, request):
            # Check request produced by ams client
            expected = {'messages': [{'attributes': {'bar1': 'baz1'}, 'data': 'Zm9vMQ=='}]}
            assert(expected["messages"][0]["data"] == "Zm9vMQ==")
            assert (expected["messages"][0]["attributes"]["bar1"]=="baz1")

            return '{"msgIds":["1"]}'

        # Execute ams client with mocked response
        with HTTMock(publish_mock):
            msg = AmsMessage(data='foo1', attributes={'bar1': 'baz1'}).dict()
            resp = self.ams.publish("topic1",msg)
            # Assert that ams client handled the json response correctly
            assert(resp["msgIds"][0]=="1")




if __name__ == '__main__':
    unittest.main()



