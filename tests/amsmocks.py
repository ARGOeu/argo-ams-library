from httmock import urlmatch, HTTMock, response
import json


class SubMocks(object):
    get_sub_urlmatch = dict(netloc="localhost",
                            path="/v1/projects/TEST/subscriptions/subscription1",
                            method="GET")
    create_subscription_urlmatch = dict(netloc="localhost",
                                        path="/v1/projects/TEST/subscriptions/subscription1",
                                        method="PUT")
    has_subscription_urlmatch = dict(netloc="localhost",
                                     path="/v1/projects/TEST/subscriptions/subscription1",
                                     method="GET")
    ack_subscription_match = dict(netloc="localhost",
                                  path="/v1/projects/TEST/subscriptions/subscription1:acknowledge",
                                  method="POST")
    getactl_subscription_urlmatch = dict(netloc="localhost",
                                         path="/v1/projects/TEST/subscriptions/subscription1:acl",
                                         method="GET")
    modifyacl_subscription_urlmatch = dict(netloc="localhost",
                                           path="/v1/projects/TEST/subscriptions/subscription1:modifyAcl",
                                           method="POST")
    get_sub_offets_urlmatch = dict(netloc="localhost",
                                   path="/v1/projects/TEST/subscriptions/subscription1:offsets",
                                   method="GET")
    modifyoffset_sub_urlmatch = dict(netloc="localhost",
                                     path="/v1/projects/TEST/subscriptions/subscription1:modifyOffset",
                                     method="POST")

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
    @urlmatch(**create_subscription_urlmatch)
    def create_subscription_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1"
        # Return two topics in json format
        return response(200,
                        '{"name": "/projects/TEST/subscriptions/subscription1",\
                        "topic":"/projects/TEST/topics/topic1",\
                        "pushConfig":{"pushEndpoint":"","retryPolicy":{}},"ackDeadlineSeconds": 10}',
                        None, None, 5, request)

    # Mock response for GET topic request
    @urlmatch(**has_subscription_urlmatch)
    def has_subscription_mock(self, url, request):
        return response(200, '{"name":"/projects/TEST/subscriptions/subscription1",\
                        "topic":"/projects/TEST/topics/topic1",\
                        "pushConfig": {"pushEndpoint": "","retryPolicy": {}},\
                        "ackDeadlineSeconds":"10"}', None, None, 5, request)

    @urlmatch(**ack_subscription_match)
    def ack_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1:acknowledge"
        # Error: library returns json in the form {"ackIds": 1221}
        assert request.body == '{"ackIds": ["1221"]}'
        # Check request produced by ams client
        return '{}'

    @urlmatch(**modifyoffset_sub_urlmatch)
    def modifyoffset_sub_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1:modifyOffset"
        assert request.body == '{"offset": 98}'
        return '{}'

    # Mock response for GET subscriptions offsets
    @urlmatch(**get_sub_offets_urlmatch)
    def getoffsets_sub_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1:offsets"
        # Return the offsets for a subscription1
        return response(200, '{"max": 79, "min": 0, "current": 78}', None, None, 5, request)

    @urlmatch(**getactl_subscription_urlmatch)
    def getacl_subscription_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1:acl"
        # Return the details of a topic in json format
        return response(200, '{"authorized_users": []}', None, None, 5, request)

    # Mock response for GET topic request
    @urlmatch(**modifyacl_subscription_urlmatch)
    def modifyacl_subscription_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/subscriptions/subscription1:modifyAcl"
        # Return the details of a topic in json format
        return response(200, '{}', None, None, 5, request)


class TopicMocks(object):
    get_topic_urlmatch = dict(netloc="localhost",
                              path="/v1/projects/TEST/topics/topic1",
                              method='GET')
    create_topic_urlmatch = dict(netloc="localhost",
                                path="/v1/projects/TEST/topics/topic1",
                                method='PUT')
    has_topic_urlmatch = dict(netloc="localhost",
                              path="/v1/projects/TEST/topics/topic1",
                              method="GET")
    list_topic_urlmatch = dict(netloc="localhost",
                               path="/v1/projects/TEST/topics", method="GET")
    getacl_topic_urlmatch = dict(netloc="localhost",
                                 path="/v1/projects/TEST/topics/topic1:acl",
                                 method="GET")
    modifyacl_topic_urlmatch = dict(netloc="localhost",
                                    path="/v1/projects/TEST/topics/topic1:modifyAcl",
                                    method="POST")

    # Mock response for PUT topic request
    @urlmatch(**create_topic_urlmatch)
    def create_topic_mock(self, url, request):
        return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

    # Mock response for GET topic request
    @urlmatch(**has_topic_urlmatch)
    def has_topic_mock(self, url, request):
        return response(200, '{"name": "/projects/TEST/topics/topic1"}', None, None, 5, request)

    @urlmatch(**get_topic_urlmatch)
    def get_topic_mock(self, url, request):
        # Return the details of a topic in json format
        return response(200, '{"name":"/projects/TEST/topics/topic1"}', None, None, 5, request)

    # Mock response for GET topics request
    @urlmatch(**list_topic_urlmatch)
    def list_topics_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/topics"
        # Return two topics in json format
        return response(200, '{"topics":[{"name":"/projects/TEST/topics/topic1"},\
                                {"name":"/projects/TEST/topics/topic2"}]}', None, None, 5, request)

    # Mock response for GET topic request
    @urlmatch(**getacl_topic_urlmatch)
    def getacl_topic_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/topics/topic1:acl"
        # Return the details of a topic in json format
        return response(200, '{"authorized_users": []}', None, None, 5, request)

    # Mock response for GET topic request
    @urlmatch(**modifyacl_topic_urlmatch)
    def modifyacl_topic_mock(self, url, request):
        assert url.path == "/v1/projects/TEST/topics/topic1:modifyAcl"
        # Return the details of a topic in json format
        return response(200, '{}', None, None, 5, request)

