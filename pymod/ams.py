import requests
import json
from amsexceptions import AmsServiceException, AmsConnectionException
from amsmsg import AmsMessage
from amstopic import AmsTopic

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
                       "sub_create": ["put", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_delete": ["delete", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_list": ["get", "https://{0}/v1/projects/{2}/subscriptions?key={1}"],
                       "sub_get": ["get", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_pull": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:pull?key={1}"],
                       "sub_ack": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:acknowledge?key={1}"]}
        self.topics = dict()

    def _create_topic_obj(self, t):
        self.topics.update({t['name']: AmsTopic(t['name'], init=self)})

    def iter_topics(self):
        self.list_topics()

        for t in self.topics.itervalues():
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

    def has_topic(self, topic):
        """Inspect if topic already exists or not

        Args:
            topic: str. Topic name
        """
        try:
            self.get_topic(topic)
            return True

        except AmsServiceException as e:
            if e.code == 404:
                return False
            else:
                raise e

        except AmsConnectionException as e:
            raise e

    def get_topic(self, topic, **reqkwargs):
        """Get the details of a selected topic.

        Args:
            topic: str. Topic name.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "topic_get", **reqkwargs)

    def publish(self, topic, msg, **reqkwargs):
        """Publish a message or list of messages to a selected topic.

        Args:
            topic: str. Topic name.
            msg: list(AmsMessage). A list with one or more messages to send.
                Each message is represented as python dictionary with mandatory data and optional attributes keys.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        if not isinstance(msg, list):
            msg = [msg]
        msg_body = json.dumps({"messages": msg})

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

        if r:
            return r
        else:
            return []

    def get_sub(self, sub, **reqkwargs):
        """Get the details of a subscription.

        Args:
            sub: str. The subscription name.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "sub_get", **reqkwargs)

    def has_sub(self, sub):
        """Inspect if subscription already exists or not

        Args:
            sub: str. The subscription name.
        """
        try:
            self.get_sub(sub)
            return True

        except AmsServiceException as e:
            if e.code == 404:
                return False
            else:
                raise e

        except AmsConnectionException as e:
            raise e

    def pull_sub(self, sub, num=1, **reqkwargs):
        """This function consumes messages from a subscription in a project
        with a POST request.

        Args:
            sub: str. The subscription name.
            num: int. The number of messages to pull.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """

        wasmax = self.get_pullopt('maxMessages')

        self.set_pullopt('maxMessages', num)
        msg_body = json.dumps(self.pullopts)

        route = self.routes["sub_pull"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))
        r = method(url, msg_body, "sub_pull", **reqkwargs)
        msgs = r['receivedMessages']

        self.set_pullopt('maxMessages', wasmax)

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

        return method(url, msg_body, "sub_ack", **reqkwargs)

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

    def create_sub(self, sub, topic, ackdeadline=10, **reqkwargs):
        """This function creates a new subscription in a project with a PUT request

        Args:
            sub: str. The subscription name.
            topic: str. The topic name.
            ackdeadline: int. It is a custom "ack" deadline (in seconds) in the subscription. If your code doesn't
                acknowledge the message in this time, the message is sent again. If you don't specify the deadline, the
                default is 10 seconds.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        msg_body = json.dumps({"topic": self.get_topic(topic)['name'].strip('/'),
                               "ackDeadlineSeconds": ackdeadline})

        route = self.routes["sub_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        return method(url, msg_body, "sub_create", **reqkwargs)

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

        return method(url, "sub_delete", **reqkwargs)

    def create_topic(self, topic, **reqkwargs):
        """This function creates a topic in a project

        Args:
            topic: str. The topic name.
            reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        route = self.routes["topic_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        return method(url, '', "topic_create", **reqkwargs)

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

        return method(url, "topic_delete", **reqkwargs)


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
        decoded = json.loads(r.content)

        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=route_name)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

    else:
        return r.json()


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
        decoded = json.loads(r.content)

        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=route_name)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

    else:
        return r.json()


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

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, route_name)

if __name__ == "__main__":
    test = ArgoMessagingService(endpoint="messaging-devel.argo.grnet.gr", token="YOUR_TOKEN", project="ARGO")
    allprojects = test.list_topics()
