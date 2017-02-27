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
                       "sub_list": ["get", "https://{0}/v1/projects/{2}/subscriptions?key={1}"],
                       "sub_get": ["get", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_pull": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:pull?key={1}"],
                       "sub_ack": ["post", "https://{0}/v1/projects/{2}/subscriptions/{4}:acknowledge?key={1}"]}

    def list_topics(self, **reqkwargs):
        """List the topics of a selected project"""
        route = self.routes["topic_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)

        return do_get(url, "topic_list", **reqkwargs)

    def get_topic(self, topic, **reqkwargs):
        """Get the details of a selected topic
        Keyword arguments:
        @param: topic Topic Name
        """
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)

        return do_get(url, "topic_get", **reqkwargs)

    def publish(self, topic, msg, **reqkwargs):
        """Publish a message to a selected topic
        Keyword arguments:
        @param: topic Topic Name
        @param: msg the message to send
        @param: attributes key pair values list of user defined attributes
        """
        msg_body = json.dumps({"messages": msg})

        route = self.routes["topic_publish"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)

        return do_post(url, msg_body, "topic_publish", **reqkwargs)

    def list_subs(self, **reqkwargs):
        route = self.routes["sub_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)

        return do_get(url, "sub_list", **reqkwargs)

    def get_sub(self, sub, **reqkwargs):
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)

        return do_get(url, "sub_get", **reqkwargs)

    def pull_sub(self, sub, num=1, **reqkwargs):
        wasmax = self.get_pullopt('maxMessages')

        self.set_pullopt('maxMessages', num)
        msg_body = json.dumps(self.pullopts)

        route = self.routes["sub_pull"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        r = do_post(url, msg_body, "sub_pull", **reqkwargs)
        msgs = r['receivedMessages']

        self.set_pullopt('maxMessages', wasmax)

        return map(lambda m: (m['ackId'], AmsMessage(b64enc=False, **m['message'])), msgs)

    def ack_sub(self, sub, ids, **reqkwargs):
        msg_body = json.dumps({"ackIds": ids})

        route = self.routes["sub_ack"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)

        return do_post(url, msg_body, "sub_ack", **reqkwargs)

    def set_pullopt(self, key, value):
        self.pullopts.update({key: str(value)})

    def get_pullopt(self, key):
        return self.pullopts[key]

def do_get(url, routeName, **reqkwargs):
    try:
        r = requests.get(url, **reqkwargs)
        decoded = json.loads(r.content)

        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=routeName)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, routeName)

    else:
        return r.json()

def do_post(url, body, routeName, **reqkwargs):
    try:
        r = requests.post(url, data=body, **reqkwargs)
        decoded = json.loads(r.content)

        if 'error' in decoded:
            raise AmsServiceException(json=decoded, request=routeName)

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise AmsConnectionException(e, routeName)

    else:
        return r.json()

if __name__ == "__main__":
    test = ArgoMessagingService(endpoint="messaging-devel.argo.grnet.gr", token="4affb0cbb75032261bcfb3e6a959fa9ba495ff", project="ARGO");
    allprojects = test.list_topics()
