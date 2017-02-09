import requests
import json
import base64
from amsexceptions import AmsHandleExceptions


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
    """List the topics of a selected project"""
        route = self.routes["topic_list"]   
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
       
        return do_get(url,"topic_list")
    
    def get_topic(self, topic):
    """Get the details of a selected topic 
    Keyword arguments:
    @param: topic Topic Name
    """
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        return do_get(url,"topic_get")
    
    def publish(self, topic, msg):
    """Publish a message to a selected topic
    Keyword arguments:
    @param: topic Topic Name
    @param: msg the message to send 
    @param: attributes key pair values list of user defined attributes
    """
        b64enc = base64.b64encode(msg)
        msg_body = {"messages": [{"data": b64enc}]}

        route = self.routes["topic_publish"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, topic)
        return do_post(url, msg_body,"topic_publish")

    def list_subs(self):
        route = self.routes["sub_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project)
        return do_get(url, "sub_list")

    def get_sub(self, sub):
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.token, self.project, "", sub)
        return do_get(url,"sub_get")


def do_get(url,routeName):
    r = requests.get(url)
    decoded = json.loads(r.content)
    if 'error' in decoded:
       raise AmsHandleExceptions(json=decoded,request=routeName)
    return r.json()


def do_post(url, body, routeName):
   
    r = requests.post(url, data=body)
    decoded = json.loads(r.content)
    if 'error' in decoded:
       raise AmsHandleExceptions(json=decoded,request=routeName)
   
    return r.json()

if __name__ == "__main__":
    test = ArgoMessagingService(endpoint="messaging-devel.argo.grnet.gr", token="4affb0cbb75032261bcfb3e6a959fa9ba495ff", project="ARGO");
    allprojects = test.list_topics()
    print allprojects
