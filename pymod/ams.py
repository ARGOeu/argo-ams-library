import requests
import json
from amsexceptions import AmsServiceException, AmsConnectionException, AmsMessageException, AmsException
from amsmsg import AmsMessage
from amstopic import AmsTopic
from amssubscription import AmsSubscription

class ArgoMessagingService(object):
    def __init__(self, endpoint, token="", project=""):
        self.endpoint = endpoint
        self.token = token
        self.project = project
        self.pullopts = {"maxMessages": "1",
                         "returnImmediately": "False"}
        # Create route list
        self.routes = {"topic_list": ["get", "https://{0}/v1/projects/{2}/topics?key={1}"],
                       "topic_get": ["get", "https://{0}/v1/projects/{2}/topics/{3}?key={1}"],
                       "topic_publish": ["post", "https://{0}/v1/projects/{2}/topics/{3}:publish?key={1}"],
                       "topic_create": ["put", "https://{0}/v1/projects/{2}/topics/{3}?key={1}"],
                       "topic_delete": ["delete", "https://{0}/v1/projects/{2}/topics/{3}?key={1}"],
                       "topic_getacl": ["get", "https://{0}/v1/projects/{2}/topics/{3}:acl?key={1}"],
                       "topic_modifyacl": ["post", "https://{0}/v1/projects/{2}/topics/{3}:modifyAcl?key={1}"],
                       "sub_create": ["put", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_delete": ["delete", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_list": ["get", "https://{0}/v1/projects/{2}/subscriptions?key={1}"],
                       "sub_get": ["get", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_pull": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:pull?key={1}"],
                       "sub_ack": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:acknowledge?key={1}"],
                       "sub_pushconfig": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:modifyPushConfig?key={1}"],
                       "sub_getacl": ["get", "https://{0}/v1/projects/{2}/subscriptions/{3}:acl?key={1}"],
                       "sub_modifyacl": ["post", "https://{0}/v1/projects/{2}/subscriptions/{3}:modifyAcl?key={1}"]}
        # Containers for topic and subscription objects
        self.topics = dict()
        self.subs = dict()

    def _create_sub_obj(self, s, topic):
        self.subs.update({s['name']: AmsSubscription(s['name'], topic,
                                                     s['pushConfig'],
                                                     s['ackDeadlineSeconds'],
                                                     init=self)})

    def _delete_sub_obj(self, s):
        del self.subs[s['name']]

    def _create_topic_obj(self, t):
        self.topics.update({t['name']: AmsTopic(t['name'], init=self)})

    def _delete_topic_obj(self, t):
        del self.topics[t['name']]

    def getacl_topic(self, topic, **reqkwargs):
        """
           Get access control lists for topic

           Args:
               topic (str): The topic name.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        topicobj = self.get_topic(topic, retobj=True)

        route = self.routes["topic_getacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "topic_getacl", **reqkwargs)

        if r:
            self.topics[topicobj.fullname].acls = r['authorized_users']
            return r
        else:
            self.topics[topicobj.fullname].acls = []
            return []

    def modifyacl_topic(self, topic, users, **reqkwargs):
        """
           Modify access control lists for topic

           Args:
               topic (str): The topic name.
               users (list): List of users that will have access to topic.
                             Empty list of users will reset access control list.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        topicobj = self.get_topic(topic, retobj=True)

        route = self.routes["topic_modifyacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        r = None
        try:
            msg_body = json.dumps({"authorized_users": users})
            r = method(url, msg_body, "topic_modifyacl", **reqkwargs)

            if r is not None:
                self.topics[topicobj.fullname].acls = users

            return True

        except AmsServiceException as e:
            raise e

        except TypeError as e:
            raise AmsServiceException(e)

    def getacl_sub(self, sub, **reqkwargs):
        """
           Get access control lists for subscription

           Args:
               sub (str): The subscription name.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        subobj = self.get_sub(sub, retobj=True)

        route = self.routes["sub_getacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, sub)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "sub_getacl", **reqkwargs)

        if r:
            self.subs[subobj.fullname].acls = r['authorized_users']
            return r
        else:
            self.subs[subobj.fullname].acls = []
            return []

    def modifyacl_sub(self, sub, users, **reqkwargs):
        """
           Modify access control lists for subscription

           Args:
               sub (str): The subscription name.
               users (list): List of users that will have access to subscription.
                             Empty list of users will reset access control list.
           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        subobj = self.get_sub(sub, retobj=True)

        route = self.routes["sub_modifyacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, sub)
        method = eval('do_{0}'.format(route[0]))

        r = None
        try:
            msg_body = json.dumps({"authorized_users": users})
            r = method(url, msg_body, "sub_modifyacl", **reqkwargs)

            if r is not None:
                self.subs[subobj.fullname].acls = users

            return True

        except AmsServiceException as e:
            raise e

        except TypeError as e:
            raise AmsServiceException(e)

    def pushconfig_sub(self, sub, push_endpoint=None, retry_policy_type='linear', retry_policy_period=300, **reqkwargs):
        """Modify push configuration of given subscription

           Args:
               sub: shortname of subscription
               push_endpoint: URL of remote endpoint that should receive messages in push subscription mode
               retry_policy_type:
               retry_policy_period:
               reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        if push_endpoint:
            push_dict = {"pushConfig": {"pushEndpoint": push_endpoint,
                                        "retryPolicy": {"type": retry_policy_type,
                                                        "period": retry_policy_period}}}
        else:
            push_dict = {"pushConfig": {}}

        msg_body = json.dumps(push_dict)
        route = self.routes["sub_pushconfig"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))
        p = method(url, msg_body, "sub_pushconfig", **reqkwargs)

        subobj = self.subs.get('/projects/{0}/subscriptions/{1}'.format(self.project, sub), False)
        if subobj:
            subobj.push_endpoint = push_endpoint
            subobj.retry_policy_type = retry_policy_type
            subobj.retry_policy_period = retry_policy_period

        return p

    def iter_subs(self, topic=None):
        """Iterate over AmsSubscription objects

        Args:
            topic: Iterate over subscriptions only associated to this topic name
        """
        self.list_subs()

        for s in self.subs.copy().itervalues():
            if topic and topic == s.topic.name:
                yield s
            elif not topic:
                yield s

    def iter_topics(self):
        """Iterate over AmsTopic objects"""

        self.list_topics()

        for t in self.topics.copy().itervalues():
            yield t

    def list_topics(self, **reqkwargs):
        """List the topics of a selected project

        Args:
            reqkwargs: keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["topic_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "topic_list", **reqkwargs)

        for t in r['topics']:
            if t['name'] not in self.topics:
                self._create_topic_obj(t)

        if r:
            return r
        else:
            return []

    def has_topic(self, topic, **reqkwargs):
        """Inspect if topic already exists or not

        Args:
            topic: str. Topic name
        """
        try:
            self.get_topic(topic, **reqkwargs)
            return True

        except AmsServiceException as e:
            if e.code == 404:
                return False
            else:
                raise e

        except AmsConnectionException as e:
            raise e

    def get_topic(self, topic, retobj=False, **reqkwargs):
        """Get the details of a selected topic.

        Args:
            topic: str. Topic name.
            retobj: Controls whether method should return AmsTopic object
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "topic_get", **reqkwargs)

        if r['name'] not in self.topics:
            self._create_topic_obj(r)

        if retobj:
            return self.topics[r['name']]
        else:
            return r

    def publish(self, topic, msg, **reqkwargs):
        """Publish a message or list of messages to a selected topic.

        Args:
            topic (str): Topic name.
            msg (list): A list with one or more messages to send.
                        Each message is represented as AmsMessage object or python
                        dictionary with at least data or one attribute key defined.
        Kwargs:
            reqkwargs: keyword argument that will be passed to underlying
                       python-requests library call.
        Return:
            dict: Dictionary with messageIds of published messages
        """
        if not isinstance(msg, list):
            msg = [msg]
        if all(isinstance(m, AmsMessage) for m in msg):
            msg = [m.dict() for m in msg]
        try:
            msg_body = json.dumps({"messages": msg})
        except TypeError as e:
            raise AmsMessageException(e)

        route = self.routes["topic_publish"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        return method(url, msg_body, "topic_publish", **reqkwargs)

    def list_subs(self, **reqkwargs):
        """Lists all subscriptions in a project with a GET request.

        Args:
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["sub_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "sub_list", **reqkwargs)

        for s in r['subscriptions']:
            if s['topic'] not in self.topics:
                self._create_topic_obj({'name': s['topic']})
            if s['name'] not in self.subs:
                self._create_sub_obj(s, self.topics[s['topic']].fullname)

        if r:
            return r
        else:
            return []

    def get_sub(self, sub, retobj=False, **reqkwargs):
        """Get the details of a subscription.

        Args:
            sub: str. The subscription name.
            retobj: Controls whether method should return AmsSubscription object
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "sub_get", **reqkwargs)

        if r['topic'] not in self.topics:
            self._create_topic_obj({'name': r['topic']})
        if r['name'] not in self.subs:
            self._create_sub_obj(r, self.topics[r['topic']].fullname)

        if retobj:
            return self.subs[r['name']]
        else:
            return r

    def has_sub(self, sub, **reqkwargs):
        """Inspect if subscription already exists or not

        Args:
            sub: str. The subscription name.
        """
        try:
            self.get_sub(sub, **reqkwargs)
            return True

        except AmsServiceException as e:
            if e.code == 404:
                return False
            else:
                raise e

        except AmsConnectionException as e:
            raise e

    def pull_sub(self, sub, num=1, return_immediately=False, **reqkwargs):
        """This function consumes messages from a subscription in a project
        with a POST request.

        Args:
            sub: str. The subscription name.
            num: int. The number of messages to pull.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """

        wasmax = self.get_pullopt('maxMessages')
        wasretim = self.get_pullopt('returnImmediately')

        self.set_pullopt('maxMessages', num)
        self.set_pullopt('returnImmediately', str(return_immediately))
        msg_body = json.dumps(self.pullopts)

        route = self.routes["sub_pull"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))
        r = method(url, msg_body, "sub_pull", **reqkwargs)
        msgs = r['receivedMessages']

        self.set_pullopt('maxMessages', wasmax)
        self.set_pullopt('returnImmediately', wasretim)

        return map(lambda m: (m['ackId'], AmsMessage(b64enc=False, **m['message'])), msgs)

    def ack_sub(self, sub, ids, **reqkwargs):
        """Messages retrieved from a pull subscription can be acknowledged by sending message with an array of ackIDs.
        The service will retrieve the ackID corresponding to the highest message offset and will consider that message
        and all previous messages as acknowledged by the consumer.

        Args:
            sub: str. The subscription name.
            ids: list(str). A list of ids of the messages to acknowledge.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """

        msg_body = json.dumps({"ackIds": ids})

        route = self.routes["sub_ack"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))
        method(url, msg_body, "sub_ack", **reqkwargs)

        return True

    def set_pullopt(self, key, value):
        """Function for setting pull options

        Args:
            key: str. The name of the pull option (ex. maxMessages, returnImmediately).Messaging specific
               names are allowed.
            value: str or int. The name of the pull option (ex. maxMessages, returnImmediately).Messaging specific names
            are allowed.
        """

        self.pullopts.update({key: str(value)})

    def get_pullopt(self, key):
        """Function for getting pull options

        Args:
            key: str. The name of the pull option (ex. maxMessages, returnImmediately).Messaging specific
               names are allowed.

        Returns:
            str. The value of the pull option
        """
        return self.pullopts[key]

    def create_sub(self, sub, topic, ackdeadline=10, push_endpoint=None,
                   retry_policy_type='linear', retry_policy_period=300, retobj=False, **reqkwargs):
        """This function creates a new subscription in a project with a PUT request

        Args:
            sub: str. The subscription name.
            topic: str. The topic name.
            ackdeadline: int. It is a custom "ack" deadline (in seconds) in the subscription. If your code doesn't
                              acknowledge the message in this time, the message is sent again. If you don't specify
                              the deadline, the default is 10 seconds.
            push_endpoint: URL of remote endpoint that should receive messages in push subscription mode
            retry_policy_type:
            retry_policy_period:
            retobj: Controls whether method should return AmsSubscription object
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        topic = self.get_topic(topic, retobj=True)

        msg_body = json.dumps({"topic": topic.fullname.strip('/'),
                               "ackDeadlineSeconds": ackdeadline})

        route = self.routes["sub_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, msg_body, "sub_create", **reqkwargs)

        if push_endpoint:
            ret = self.pushconfig_sub(sub, push_endpoint, retry_policy_type, retry_policy_period)
            r['pushConfig'] = {"pushEndpoint": push_endpoint,
                               "retryPolicy": {"type": retry_policy_type,
                                               "period": retry_policy_period}}

        if r['name'] not in self.subs:
            self._create_sub_obj(r, topic.fullname)

        if retobj:
            return self.subs[r['name']]
        else:
            return r

    def delete_sub(self, sub, **reqkwargs):
        """This function deletes a selected subscription in a project

        Args:
            sub: str. The subscription name.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["sub_delete"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "sub_delete", **reqkwargs)

        sub_fullname = "/projects/{0}/subscriptions/{1}".format(self.project, sub)
        if sub_fullname in self.subs:
            self._delete_sub_obj({'name': sub_fullname})

        return r

    def topic(self, topic, **reqkwargs):
        """Function create a topic in a project. It's wrapper around few
           methods defined in client class. Method will ensure that AmsTopic
           object is returned either by fetching existing one or creating
           a new one in case it doesn't exist.

           Args:
               topic (str): The topic name
           Kwargs:
            reqkwargs: keyword argument that will be passed to underlying
                       python-requests library call.
           Return:
               object (AmsTopic)
        """
        try:
            if self.has_topic(topic, **reqkwargs):
                return self.get_topic(topic, retobj=True, **reqkwargs)
            else:
                return self.create_topic(topic, retobj=True, **reqkwargs)

        except AmsException as e:
            raise e

    def create_topic(self, topic, retobj=False, **reqkwargs):
        """This function creates a topic in a project

        Args:
            topic: str. The topic name.
            retobj: Controls whether method should return AmsTopic object
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["topic_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, '', "topic_create", **reqkwargs)

        if r['name'] not in self.topics:
            self._create_topic_obj(r)

        if retobj:
            return self.topics[r['name']]
        else:
            return r

    def delete_topic(self, topic, **reqkwargs):
        """ This function deletes a topic in a project

        Args:
            topic: str. The topic name.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["topic_delete"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        r = method(url, "topic_delete", **reqkwargs)

        topic_fullname = "/projects/{0}/topics/{1}".format(self.project, topic)
        if topic_fullname in self.topics:
            self._delete_topic_obj({'name': topic_fullname})

        return r


def do_get(url, route_name, **reqkwargs):
    """This global function supports all the GET requests. Used for (topics,
    subscriptions, messages). The requests library is used for the final GET
    request.

    Args:
        url: str. The final messaging service endpoint
        route_name: str. The name of the route to follow selected from the route list
        reqkwargs: keyword argument that will be passed to underlying python-requests library call.
    """
    # try to send a GET request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the get request based on requests.
        r = requests.get(url, **reqkwargs)
        decoded = json.loads(r.content)
        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=route_name)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

    else:
        return r.json()


def do_put(url, body, route_name, **reqkwargs):
    """This global function supports all the PUT requests. Used for (topics,
    subscriptions, messages). The requests library is used for the final PUT
    request.

    Args:
        url: str. The final messaging service endpoint
        body: dict. Body the post data to send based on the PUT request. The post data is always in json format.
        route_name: str. The name of the route to follow selected from the route list
        reqkwargs: keyword argument that will be passed to underlying python-requests library call.
    """
    # try to send a PUT request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the post request based on requests.
        r = requests.put(url, data=body, **reqkwargs)
        decoded = json.loads(r.content) if r.content else {}

        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=route_name)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

    else:
        return r.json() if decoded else {}


def do_post(url, body, route_name, **reqkwargs):
    """This global function supports all the POST requests. Used for (topics,
       subscriptions, messages). The requests library is used for the final POST
       request.

    Args:
        url: str. The final messaging service endpoint
        body: dict. Body the post data to send based on the PUT request. The post data is always in json format.
        route_name: str. The name of the route to follow selected from the route list
        reqkwargs: keyword argument that will be passed to underlying python-requests library call.
    """
    # try to send a Post request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the post request based on requests.
        r = requests.post(url, data=body, **reqkwargs)
        decoded = json.loads(r.content) if r.content else {}

        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=route_name)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

    else:
        return r.json() if decoded else {}


def do_delete(url, route_name, **reqkwargs):
    """A global delete function that is used to make the appropriate request.
    Used for (topics, subscriptions). The requests library is used for the final
    delete request.

    Args:
        url: str. The final messaging service endpoint
        route_name: str. The name of the route to follow selected from the route list
        reqkwargs: keyword argument that will be passed to underlying python-requests library call.
    """
    # try to send a delete request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the delete request based on requests.
        r = requests.delete(url, **reqkwargs)

        if r.status_code != 200:
            decoded = json.loads(r.content)
            # if the result returns an error code an exception is raised.
            if 'error' in decoded:
                raise AmsServiceException(json=decoded, request=route_name)
        else:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

if __name__ == "__main__":
    test = ArgoMessagingService(endpoint="messaging-devel.argo.grnet.gr", token="YOUR_TOKEN", project="ARGO")
    allprojects = test.list_topics()
