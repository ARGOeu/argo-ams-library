import requests
import json
import base64


class ArgoMessagingService:
    def __init__(self, endpoint, token="", project=""):
        self.endpoint = endpoint
        self.token = token
        self.project = project

        # Create route list
        self.routes = {"topic_list": ["get", "https://{0}/v1/projects/{2}/topics?key={1}"],
                       "topic_get": ["get", "https://{0}/v1/projects/{2}/topics/{3}?key={1}"],
                       "topic_publish": ["post", "https://{0}/v1/projects/{2}/topics/{3}:publish?key={1}"],
                       "sub_list": ["get", "https://{0}/v1/projects/{2}/subscriptions?key={1}"],
                       "sub_get": ["get", "https://{0}/v1/projects/{2}/subscriptions/{4}?key={1}"],
                       "sub_pull": ["get", "https://{0}/v1/projects/{2}/subscriptions/{4}:pull?key={1}"],
                       "sub_ack": ["get", "https://{0}/v1/projects/{2}/subscriptions/{4}:acknowledge?key={1}"]}

    def list_topics(self):
        route = self.routes["topic_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        return do_get(url)

    def get_topic(self, topic):
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        return do_get(url)

    def publish(self, topic, msg):
        b64enc = base64.b64encode(msg)
        msg_body = {"messages": [{"data": b64enc}]}

        route = self.routes["topic_publish"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        return do_post(url, msg_body)

    def list_subs(self):
        route = self.routes["sub_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        return do_get(url)

    def get_sub(self, sub):
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        return do_get(url)


def do_get(url):
    r = requests.get(url)
    return r.json()


def do_post(url, body):
    print body
    r = requests.post(url, data=body)
    return r.json()

