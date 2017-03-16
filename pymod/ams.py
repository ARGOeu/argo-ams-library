import requests
import json
import base64
from amsexceptions import AmsServiceException, AmsConnectionException
from amsmsg import AmsMessage

class ArgoMessagingService:
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

    def list_topics(self, **reqkwargs):
        """List the topics of a selected project
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["topic_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "topic_list", **reqkwargs)

    def has_topic(self, topic, **reqkwargs):
        """Inspect if topic already exists or not
        Keyword arguments:
        @param: topic Topic Name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        try:
            self.get_topic(topic)
            return True

        except AmsServiceException as e:
            if e.code == 404:
                return False
            else:
                return True

        except AmsConnectionException as e:
            raise e

    def get_topic(self, topic, **reqkwargs):
        """Get the details of a selected topic
        Keyword arguments:
        @param: topic Topic Name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "topic_get", **reqkwargs)

    def publish(self, topic, msg, **reqkwargs):
        """Publish a message or list of messages to a selected topic
        Keyword arguments:
        @param: topic Topic Name
        @param: msg the message or list of messages to send. Each message is
                represented as python dictionary with mandatory data and
                optional attributes keys.
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
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
        """Lists all subscriptions in a project with a GET request
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["sub_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        method = eval('do_{0}'.format(route[0]))
        r = method(url, "sub_list", **reqkwargs)
        if r:
            return r['subscriptions']
        else:
            return []

    def get_sub(self, sub, **reqkwargs):
        """Get the details of a subscription.
        @param: sub the Subscription name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "sub_get", **reqkwargs)


    def has_sub(self, sub, **reqkwargs):
        """Inspect if subscription already exists or not
        @param: sub the Subscription name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        try:
            self.get_sub(sub)
            return True

        except AmsServiceException as e:
            if e.code == 404:
                return False
            else:
                return True

        except AmsConnectionException as e:
            raise e

    def pull_sub(self, sub, num=1, **reqkwargs):
        """This function consumes messages from a subscription in a project
        with a POST request.
        @param: sub the Subscription name.
        @param: num the number of messages to pull.
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
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
        """Messages retrieved from a pull subscription can be acknowledged by
        sending message with an array of ackIDs. The service will retrieve the
        ackID corresponding to the highest message offset and will consider
        that message and all previous messages as acknowledged by the consumer.
        @param: sub The subscription name to consume messages
        @param: ids The ids of the messages to acknowledge
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        msg_body = json.dumps({"ackIds": ids})

        route = self.routes["sub_ack"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        return method(url, msg_body, "sub_ack", **reqkwargs)

    def set_pullopt(self, key, value):
        """Function for setting pull options
        @param: key the name of the pull option (ex. maxMessages,
                returnImmediately).Messaging specific names are allowed.
        @param: value of the pull option
        """

        self.pullopts.update({key: str(value)})

    def get_pullopt(self, key):
        """Function for getting pull options
        @param: key the name of the pull option (ex. maxMessages,
                returnImmediately). Messaging specific names are allowed.
        @param: value of the pull option
        """
        return self.pullopts[key]

    def create_sub(self, sub, topic, ackdeadline=10, **reqkwargs):
        """ This function creates a new subscription in a project with a PUT request
        @param: sub the Subscription name
        @param: topic the Topics name
        @param: ackdeadline is the ackDeadlineSeconds. It is a custom "ack"
                deadline in the subscription. if your code doesn't acknowledge the
                message in this time, the message is sent again. If you don't specify
                the deadline, the default is 10 seconds.
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        msg_body = json.dumps({"topic": self.get_topic(topic)['name'].strip('/'),
                               "ackDeadlineSeconds": ackdeadline})
        route = self.routes["sub_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        return method(url, msg_body, "sub_create", **reqkwargs)

    def delete_sub(self, sub, **reqkwargs):
        """ This function deletes a selected subscription in a project
        @param: sub the Subscription name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["sub_delete"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "sub_delete", **reqkwargs)

    def create_topic(self, topic, **reqkwargs):
        """ This function creates a topic in a project
        @param: topic the Topics name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["topic_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        return method(url, '', "topic_create", **reqkwargs)

    def delete_topic(self, topic, **reqkwargs):
        """ This function deletes a topic in a project
        @param: topic the Topics name
        @param: reqkwargs keyword argument that will be passed to underlying
                python-requests library call
        """
        route = self.routes["topic_delete"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        method = eval('do_{0}'.format(route[0]))

        return method(url, "topic_delete", **reqkwargs)

def do_get(url, routeName, **reqkwargs):
    """This global function supports all the GET requests. Used for (topics,
    subscriptions, messages). The requests library is used for the final GET
    request.
    @param: url the final messaging endpoint.
    @param: routeName the name of the route to follow selected from the route list
    @param: reqkwargs keyword argument that will be passed to underlying
            python-requests library call
    """
    # try to send a GET request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the get request based on requests.
        r = requests.get(url, **reqkwargs)
        decoded = json.loads(r.content)
        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=routeName)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, routeName)

    else:
        return r.json()

def do_put(url, body, routeName, **reqkwargs):
    """ This global function supports all the PUT requests. Used for (topics,
    subscriptions, messages). The requests library is used for the final PUT
    request.
    @param: body the post data to send based on the PUT request. The post data
            is always in json format.
    @param: url the final messaging endpoint.
    @param: routeName the name of the route to follow selected from the route list
    @param: reqkwargs keyword argument that will be passed to underlying
            python-requests library call
    """
    # try to send a PUT request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the post request based on requests.
        r = requests.put(url, data=body, **reqkwargs)
        decoded = json.loads(r.content)

        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=routeName)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, routeName)

    else:
        return r.json()

def do_post(url, body, routeName, **reqkwargs):
    """This global function supports all the POST requests. Used for (topics,
       subscriptions, messages). The requests library is used for the final POST
       request.
    @param: url the final messaging endpoint.
    @param: body the post data to send based on the post request. The post data
            is always in json format.
    @param: routeName the name of the route to follow selected from the route list
    @param: reqkwargs keyword argument that will be passed to underlying
            python-requests library call
    """
    # try to send a Post request to the messaging service.
    # if a connection problem araises a Connection error exception is raised.
    try:
        # the post request based on requests.
        r = requests.post(url, data=body, **reqkwargs)
        decoded = json.loads(r.content)

        # if the result returns an error code an exception is raised.
        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=routeName)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, routeName)

    else:
        return r.json()

def do_delete(url, routeName, **reqkwargs):
    """A global delete function that is used to make the appropriate request.
    Used for (topics, subscriptions). The requests library is used for the final
    delete request.
    @param: url the final messaging endpoint
    @param: routeName the name of the route to follow selected from the route list
    @param: reqkwargs keyword argument that will be passed to underlying
            python-requests library call
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
                raise AmsServiceException(json=decoded, request=routeName)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, routeName)

if __name__ == "__main__":
    test = ArgoMessagingService(endpoint="messaging-devel.argo.grnet.gr", token="YOUR_TOKEN", project="ARGO");
    allprojects = test.list_topics()
