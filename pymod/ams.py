import json
import logging
import logging.handlers
import requests
import socket
import sys
import datetime
import time

from .amsexceptions import (AmsServiceException, AmsConnectionException,
                            AmsMessageException, AmsException,
                            AmsTimeoutException, AmsBalancerException)
from .amsmsg import AmsMessage
from .amstopic import AmsTopic
from .amssubscription import AmsSubscription
from .amsuser import AmsUser, AmsUserPage, AmsUserProject

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

log = logging.getLogger(__name__)


class AmsHttpRequests(object):
    """Class encapsulates methods used by ArgoMessagingService.

       Each method represent HTTP request made to AMS with the help of requests
       library. service error handling is implemented according to HTTP
       status codes returned by service and the balancer.
    """

    def __init__(self, endpoint, authn_port, token="", cert="", key=""):
        self.endpoint = endpoint
        self.authn_port = authn_port
        self.token = token

        # Create route list
        self.routes = {
            # topic api calls
            "topic_list": ["get", "https://{0}/v1/projects/{1}/topics"],
            "topic_get": ["get", "https://{0}/v1/projects/{1}/topics/{2}"],
            "topic_publish": ["post", "https://{0}/v1/projects/{1}/topics/{2}:publish"],
            "topic_create": ["put", "https://{0}/v1/projects/{1}/topics/{2}"],
            "topic_delete": ["delete", "https://{0}/v1/projects/{1}/topics/{2}"],
            "topic_getacl": ["get", "https://{0}/v1/projects/{1}/topics/{2}:acl"],
            "topic_modifyacl": ["post", "https://{0}/v1/projects/{1}/topics/{2}:modifyAcl"],

            # subscription api calls
            "sub_create": ["put", "https://{0}/v1/projects/{1}/subscriptions/{2}"],
            "sub_delete": ["delete", "https://{0}/v1/projects/{1}/subscriptions/{2}"],
            "sub_list": ["get", "https://{0}/v1/projects/{1}/subscriptions"],
            "sub_get": ["get", "https://{0}/v1/projects/{1}/subscriptions/{2}"],
            "sub_pull": ["post", "https://{0}/v1/projects/{1}/subscriptions/{2}:pull"],
            "sub_ack": ["post", "https://{0}/v1/projects/{1}/subscriptions/{2}:acknowledge"],
            "sub_pushconfig": ["post", "https://{0}/v1/projects/{1}/subscriptions/{2}:modifyPushConfig"],
            "sub_getacl": ["get", "https://{0}/v1/projects/{1}/subscriptions/{2}:acl"],
            "sub_modifyacl": ["post", "https://{0}/v1/projects/{1}/subscriptions/{2}:modifyAcl"],
            "sub_offsets": ["get", "https://{0}/v1/projects/{1}/subscriptions/{2}:offsets"],
            "sub_mod_offset": ["post", "https://{0}/v1/projects/{1}/subscriptions/{2}:modifyOffset"],
            "sub_timeToOffset": ["get", "https://{0}/v1/projects/{1}/subscriptions/{2}:timeToOffset?time={3}"],

            # miscellaneous api calls about metrics,version,status
            "api_status": ["get", "https://{0}/v1/status"],
            "api_metrics": ["get", "https://{0}/v1/metrics"],
            "api_va_metrics": ["get", "https://{0}/v1/metrics/va_metrics"],
            "api_version": ["get", "https://{0}/v1/version"],
            "api_usage_report": ["get", "https://{0}/v1/users/usageReport"],

            # user api calls
            "user_create": ["post", "https://{0}/v1/users/{1}"],
            "user_update": ["put", "https://{0}/v1/users/{1}"],
            "user_get": ["get", "https://{0}/v1/users/{1}"],
            "user_get_by_token": ["get", "https://{0}/v1/users:byToken/{1}"],
            "user_get_by_uuid": ["get", "https://{0}/v1/users:byUUID/{1}"],
            "user_get_profile": ["get", "https://{0}/v1/users/profile"],
            "users_list": ["get", "https://{0}/v1/users"],
            "user_delete": ["delete", "https://{0}/v1/users/{1}"],
            "user_refresh_token": ["post", "https://{0}/v1/users/{1}:refreshToken"],

            # project api calls
            "project_add_member": ["post", "https://{0}/v1/projects/{1}/members/{2}:add"],
            "project_get_member": ["get", "https://{0}/v1/projects/{1}/members/{2}"],
            "project_create_member": ["post", "https://{0}/v1/projects/{1}/members/{2}"],
            "project_remove_member": ["post", "https://{0}/v1/projects/{1}/members/{2}:remove"],
            "project_create": ["post", "https://{0}/v1/projects/{1}"],
            "project_update": ["put", "https://{0}/v1/projects/{1}"],
            "project_get": ["get", "https://{0}/v1/projects/{1}"],
            "project_delete": ["delete", "https://{0}/v1/projects/{1}"],

            "auth_x509": ["get", "https://{0}:{1}/v1/service-types/ams/hosts/{0}:authx509"],
        }

        # HTTP error status codes returned by AMS according to:
        # http://argoeu.github.io/messaging/v1/api_errors/
        self.ams_errors_route = {
            "topic_create": ["put", set([409, 401, 403])],
            "topic_list": ["get", set([400, 401, 403, 404])],
            "topic_delete": ["delete", set([401, 403, 404])],
            "topic_get": ["get", set([404, 401, 403])],
            "topic_modifyacl": ["post", set([400, 401, 403, 404])],
            "topic_publish": ["post", set([413, 401, 403])],

            "sub_create": ["put", set([400, 409, 408, 401, 403])],
            "sub_get": ["get", set([404, 401, 403])],
            "sub_mod_offset": ["post", set([400, 401, 403, 404])],
            "sub_ack": ["post", set([408, 400, 401, 403, 404])],
            "sub_pushconfig": ["post", set([400, 401, 403, 404])],
            "sub_pull": ["post", set([400, 401, 403, 404])],
            "sub_timeToOffset": ["get", set([400, 401, 403, 404, 409])],

            "user_create": ["post", set([400, 401, 403, 404, 409])],
            "user_update": ["post", set([400, 401, 403, 404, 409])],
            "user_get": ["get", set([400, 401, 403, 404])],
            "user_get_by_token": ["get", set([400, 401, 403, 404])],
            "user_get_by_uuid": ["get", set([400, 401, 403, 404])],
            "user_get_profile": ["get", set([400, 401, 403, 404])],
            "users_list": ["get", set([401, 403])],
            "user_delete": ["delete", set([401, 403, 404])],
            "user_refresh_token": ["post", set([401, 403, 404])],

            "api_status": ["get", set([401, 403])],
            "api_metrics": ["get", set([401, 403])],
            "api_va_metrics": ["get", set([400, 401, 403, 404])],
            "api_version": ["get", set([401, 403])],
            "api_usage_report": ["get", set([400, 401, 403])],

            "project_add_member": ["post", set([400, 401, 403, 404, 409])],
            "project_get_member": ["get", set([400, 401, 403, 404])],
            "project_create_member": ["post", set([400, 401, 403, 404, 409])],
            "project_remove_member": ["get", set([401, 403, 404])],
            "project_create": ["post", set([400, 401, 403, 409])],
            "project_update": ["put", set([400, 401, 403, 404, 409])],
            "project_get": ["get", set([401, 403, 404])],
            "project_delete": ["delete", set([401, 403, 404])],

            "auth_x509": ["post", set([400, 401, 403, 404])]}

        # https://cbonte.github.io/haproxy-dconv/1.8/configuration.html#1.3
        self.balancer_errors_route = {"sub_ack": ["post", set([500, 502, 503, 504])],
                                      "sub_pull": ["post", set([500, 502, 503, 504])],
                                      "topic_publish": ["post", set([500, 502, 503, 504])]}

        # determine the token to be used
        self.assign_token(token, cert, key)

    def assign_token(self, token, cert, key):
        """Assign a token to the ams object

           Args:
               token(str): a valid ams token
               cert(str): a path to a valid certificate file
               key(str): a path to the associated key file for the provided certificate
        """

        # check if a token has been provided
        if token != "":
            return

        try:
            # otherwise use the provided certificate to retrieve it
            self.token = self.auth_via_cert(cert, key)
        except AmsServiceException as e:
            # if the request send to authn didn't contain an x509 cert, that means that there was also no token provided
            # when initializing the ArgoMessagingService object, since we only try to authenticate through authn
            # when no token was provided

            if e.msg == 'While trying the [auth_x509]: No certificate provided.':
                refined_msg = "No certificate provided. No token provided."
                errormsg = self._error_dict(refined_msg, e.code)
                raise AmsServiceException(json=errormsg, request="auth_x509")
            raise e

    def auth_via_cert(self, cert, key, **reqkwargs):
        """Retrieve an ams token based on the provided certificate

            Args:
                cert(str): a path to a valid certificate file
                key(str): a path to the associated key file for the provided certificate

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        if cert == "" and key == "":
            errord = self._error_dict("No certificate provided.", 400)
            raise AmsServiceException(json=errord, request="auth_x509")

        # create the certificate tuple needed by the requests library
        reqkwargs = {"cert": (cert, key)}

        route = self.routes["auth_x509"]

        # Compose url
        url = route[1].format(self.endpoint, self.authn_port)
        method = getattr(self, 'do_{0}'.format(route[0]))

        try:
            r = method(url, "auth_x509", **reqkwargs)
            # if the `token` field was not found in the response, raise an error
            if "token" not in r:
                errord = self._error_dict("Token was not found in the response. Response: " + str(r), 500)
                raise AmsServiceException(json=errord, request="auth_x509")
            return r["token"]
        except (AmsServiceException, AmsConnectionException) as e:
            raise e

    def _error_dict(self, response_content, status):
        error_dict = dict()

        try:
            if (response_content and sys.version_info < (3, 6,) and
                    isinstance(response_content, bytes)):
                response_content = response_content.decode()
            error_dict = json.loads(response_content) if response_content else {}
        except ValueError:
            error_dict = {'error': {'code': status, 'message': response_content}}

        return error_dict

    def _gen_backoff_time(self, try_number, backoff_factor):
        for i in range(0, try_number):
            value = backoff_factor * (2 ** (i - 1))
            yield value

    def _retry_make_request(self, url, body=None, route_name=None, retry=0,
                            retrysleep=60, retrybackoff=None, **reqkwargs):
        """Wrapper around _make_request() that decides whether should request
        be retried or not.

           Two request retry modes are available:
               1) static sleep - fixed amount of seconds to sleep between
                  request attempts
               2) backoff - each next sleep before request attempt is
                  exponentially longer

           If enabled, request will be retried in the following occassions:
               * timeouts from AMS (HTTP 408) or load balancer (HTTP 408 and 504)
               * load balancer HTTP 502, 503
               * connection related problems in the lower network layers

           Default behaviour is no retry attempts. If both, retry and
           retrybackoff are enabled, retrybackoff will take precedence.

           Args:
               url: str. The final messaging service endpoint
               body: dict. Payload of the request
               route_name: str. The name of the route to follow selected from the route list
               retry: int. Number of request retries before giving up. Default
                           is 0 meaning no further request retry will be made
                           after first unsuccesfull request.
               retrysleep: int. Static number of seconds to sleep before next
                           request attempt
               retrybackoff: int. Backoff factor to apply between each request
                             attempts
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        i = 1
        timeout = reqkwargs.get('timeout', 0)

        saved_exp = None
        if retrybackoff:
            try:
                return self._make_request(url, body, route_name, **reqkwargs)
            except (AmsBalancerException, AmsConnectionException,
                    AmsTimeoutException) as e:
                for sleep_secs in self._gen_backoff_time(retry, retrybackoff):
                    try:
                        return self._make_request(url, body, route_name, **reqkwargs)
                    except (AmsBalancerException, AmsConnectionException,
                            AmsTimeoutException) as e:
                        saved_exp = e
                        time.sleep(sleep_secs)
                        if timeout:
                            log.warning(
                                'Backoff retry #{0} after {1} seconds, connection timeout set to {2} seconds - {3}: {4}'.format(
                                    i, sleep_secs, timeout, self.endpoint, e))
                        else:
                            log.warning(
                                'Backoff retry #{0} after {1} seconds - {2}: {3}'.format(i, sleep_secs, self.endpoint,
                                                                                         e))
                    finally:
                        i += 1
                else:
                    if saved_exp:
                        raise saved_exp
                    else:
                        raise e

        else:
            while i <= retry + 1:
                try:
                    return self._make_request(url, body, route_name, **reqkwargs)
                except (AmsBalancerException, AmsConnectionException, AmsTimeoutException) as e:
                    if i == retry + 1:
                        raise e
                    else:
                        time.sleep(retrysleep)
                        if timeout:
                            log.warning(
                                'Retry #{0} after {1} seconds, connection timeout set to {2} seconds - {3}: {4}'.format(
                                    i, retrysleep, timeout, self.endpoint, e))
                        else:
                            log.warning(
                                'Retry #{0} after {1} seconds - {2}: {3}'.format(i, retrysleep, self.endpoint, e))
                finally:
                    i += 1

    def _make_request(self, url, body=None, route_name=None, **reqkwargs):
        """Common method for PUT, GET, POST HTTP requests with appropriate
           service error handling by differing between AMS and load balancer
           erroneous behaviour.
        """
        m = self.routes[route_name][0]
        decoded = None
        try:
            # the get request based on requests.

            # populate all requests with the x-api-key header
            # except the authn mapping call
            if route_name != "auth_x509":
                # if there is no defined headers dict in the reqkwargs, introduce it
                if "headers" not in reqkwargs:
                    headers = {
                        "x-api-key": self.token
                    }
                    reqkwargs["headers"] = headers
                else:
                    # if the there are already other headers defined, just append the x-api-key one
                    reqkwargs["headers"]["x-api-key"] = self.token

            reqmethod = getattr(requests, m)
            r = reqmethod(url, data=body, **reqkwargs)

            content = r.content
            status_code = r.status_code

            if (content and sys.version_info < (3, 6,) and isinstance(content,
                                                                      bytes)):
                content = content.decode()

            if status_code == 200:
                decoded = self._error_dict(content, status_code)

            # handle authnz related errors for all calls
            elif status_code == 401 or status_code == 403:
                raise AmsServiceException(json=self._error_dict(content,
                                                                status_code),
                                          request=route_name)

            elif status_code == 408 or (status_code == 504 and route_name in
                                        self.balancer_errors_route):
                raise AmsTimeoutException(json=self._error_dict(content,
                                                                status_code),
                                          request=route_name)

            # handle errors from AMS
            elif (status_code != 200 and status_code in
                  self.ams_errors_route[route_name][1]):
                raise AmsServiceException(json=self._error_dict(content,
                                                                status_code),
                                          request=route_name)

            # handle errors coming from load balancer
            elif (status_code != 200 and route_name in
                  self.balancer_errors_route and status_code in
                  self.balancer_errors_route[route_name][1]):
                raise AmsBalancerException(json=self._error_dict(content,
                                                                 status_code),
                                           request=route_name)

            # handle any other erroneous behaviour by raising exception
            else:
                raise AmsServiceException(json=self._error_dict(content,
                                                                status_code),
                                          request=route_name)

        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                socket.error) as e:
            raise AmsConnectionException(e, route_name)

        else:
            return decoded if decoded else {}

    def do_get(self, url, route_name, **reqkwargs):
        """Method supports all the GET requests.

           Used for (topics, subscriptions, users, messages).

           Args:
               url: str. The final messaging service endpoint
               route_name: str. The name of the route to follow selected from the route list
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        # try to send a GET request to the messaging service.
        # if a connection problem araises a Connection error exception is raised.
        try:
            return self._retry_make_request(url,
                                            body=None,
                                            route_name=route_name,
                                            **reqkwargs)
        except AmsException as e:
            raise e

    def do_put(self, url, body, route_name, **reqkwargs):
        """Method supports all the PUT requests.

           Used for (topics, subscriptions, messages).

           Args:
               url: str. The final messaging service endpoint
               body: dict. Body the post data to send based on the PUT request.
                           The post data is always in json format.
               route_name: str. The name of the route to follow selected from
                           the route list
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        # try to send a PUT request to the messaging service.
        # if a connection problem arises a Connection error exception is raised.
        try:
            return self._retry_make_request(url, body=body,
                                            route_name=route_name, **reqkwargs)
        except AmsException as e:
            raise e

    def do_post(self, url, body, route_name, retry=0, retrysleep=60,
                retrybackoff=None, **reqkwargs):
        """Method supports all the POST requests.

           Used for (topics, subscriptions, users, messages).

           Args:
               url: str. The final messaging service endpoint
               body: dict. Body the post data to send based on the PUT request.
                     The post data is always in json format.
               route_name: str. The name of the route to follow selected from
                           the route list
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        # try to send a Post request to the messaging service.
        # if a connection problem araises a Connection error exception is raised.
        try:
            return self._retry_make_request(url, body=body,
                                            route_name=route_name, retry=retry,
                                            retrysleep=retrysleep,
                                            retrybackoff=retrybackoff,
                                            **reqkwargs)
        except AmsException as e:
            raise e

    def do_delete(self, url, route_name, retry=0, retrysleep=60,
                  retrybackoff=None, **reqkwargs):
        """Delete method that is used to make the appropriate request.

           Used for (topics, subscriptions).

           Args:
               url: str. The final messaging service endpoint
               route_name: str. The name of the route to follow selected from the route list
               reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """
        # try to send a delete request to the messaging service.

        try:
            return self._retry_make_request(url, body=None,
                                            route_name=route_name, retry=retry,
                                            retrysleep=retrysleep,
                                            retrybackoff=retrybackoff,
                                            **reqkwargs)
        except AmsException as e:
            raise e


class ArgoMessagingService(AmsHttpRequests):
    """Class is entry point for client code.

       Class abstract Argo Messaging Service by covering all available HTTP API
       calls that are wrapped in series of methods.
    """

    def __init__(self, endpoint, token="", project="", cert="", key="", authn_port=8443):
        super(ArgoMessagingService, self).__init__(endpoint, authn_port, token, cert, key)
        self.project = project
        self.pullopts = {"maxMessages": "1",
                         "returnImmediately": "false"}
        # Containers for topic and subscription objects
        self.topics = OrderedDict()
        self.subs = OrderedDict()

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
        """Get access control lists for topic

           Args:
               topic (str): The topic name.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        topicobj = self.get_topic(topic, retobj=True, **reqkwargs)

        route = self.routes["topic_getacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, topic)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, "topic_getacl", **reqkwargs)

        if r:
            self.topics[topicobj.fullname].acls = r['authorized_users']
            return r
        else:
            self.topics[topicobj.fullname].acls = []
            return []

    def modifyacl_topic(self, topic, users, **reqkwargs):
        """Modify access control lists for topic

           Args:
               topic (str): The topic name.
               users (list): List of users that will have access to topic.
                             Empty list of users will reset access control list.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        topicobj = self.get_topic(topic, retobj=True, **reqkwargs)

        route = self.routes["topic_modifyacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, topic)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = None
        try:
            msg_body = json.dumps({"authorized_users": users})
            r = method(url, msg_body, "topic_modifyacl", **reqkwargs)

            if r is not None:
                self.topics[topicobj.fullname].acls = users

            return True

        except (AmsServiceException, AmsConnectionException) as e:
            raise e

    def getacl_sub(self, sub, **reqkwargs):
        """Get access control lists for subscription

           Args:
               sub (str): The subscription name.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        subobj = self.get_sub(sub, retobj=True, **reqkwargs)

        route = self.routes["sub_getacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, "sub_getacl", **reqkwargs)

        if r:
            self.subs[subobj.fullname].acls = r['authorized_users']
            return r
        else:
            self.subs[subobj.fullname].acls = []
            return []

    def getoffsets_sub(self, sub, offset='all', **reqkwargs):
        """Retrieve the current positions of min,max and current offsets.

           Args:
               sub (str): The subscription name.
               offset(str): The name of the offset.If not specified, it will return all three of them as a dict.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["sub_offsets"]

        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))
        r = method(url, "sub_offsets", **reqkwargs)
        try:
            if offset != 'all':
                return r[offset]
            return r
        except KeyError as e:
            errormsg = {'error': {'message': str(e) + " is not valid offset position"}}
            raise AmsServiceException(json=errormsg, request="sub_offsets")

    def time_to_offset_sub(self, sub, timestamp, **reqkwargs):
        """Retrieve the closest(greater than) available offset to the given timestamp.

           Args:
               sub (str): The subscription name.
               timestamp(datetime.datetime): The timestamp of the offset we are looking for.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["sub_timeToOffset"]
        method = getattr(self, 'do_{0}'.format(route[0]))

        time_in_string = ""

        if isinstance(timestamp, datetime.datetime):
            if timestamp.microsecond != 0:
                time_in_string = timestamp.isoformat()[:-3] + "Z"
            else:
                time_in_string = timestamp.strftime("%Y-%m-%d %H:%M:%S.000Z")

        # Compose url
        url = route[1].format(self.endpoint, self.project, sub, time_in_string)

        try:
            r = method(url, "sub_timeToOffset", **reqkwargs)
            return r["offset"]
        except AmsServiceException as e:
            raise e

    def modifyoffset_sub(self, sub, move_to, **reqkwargs):
        """Modify the position of the current offset.

           Args:
               sub (str): The subscription name.
               move_to(int): Position to move the offset.

           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["sub_mod_offset"]
        method = getattr(self, 'do_{0}'.format(route[0]))

        if not isinstance(move_to, int):
            move_to = int(move_to)

        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)

        # Request body
        data = {"offset": move_to}
        try:
            r = method(url, json.dumps(data), "sub_mod_offset", **reqkwargs)
            return r
        except AmsServiceException as e:
            raise e

    def modifyacl_sub(self, sub, users, **reqkwargs):
        """Modify access control lists for subscription

           Args:
               sub (str): The subscription name.
               users (list): List of users that will have access to subscription.
                             Empty list of users will reset access control list.
           Kwargs:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        subobj = self.get_sub(sub, retobj=True, **reqkwargs)

        route = self.routes["sub_modifyacl"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = None
        try:
            msg_body = json.dumps({"authorized_users": users})
            r = method(url, msg_body, "sub_modifyacl", **reqkwargs)

            if r is not None:
                self.subs[subobj.fullname].acls = users

            return True

        except (AmsServiceException, AmsConnectionException) as e:
            raise e

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
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))
        p = method(url, msg_body, "sub_pushconfig", **reqkwargs)

        subobj = self.subs.get('/projects/{0}/subscriptions/{1}'.format(self.project, sub), False)
        if subobj:
            subobj.push_endpoint = push_endpoint
            subobj.retry_policy_type = retry_policy_type
            subobj.retry_policy_period = retry_policy_period

        return p

    def iter_subs(self, topic=None, **reqkwargs):
        """Iterate over AmsSubscription objects

           Args:
               topic: Iterate over subscriptions only associated to this topic name
        """
        self.list_subs(**reqkwargs)

        try:
            values = self.subs.copy().itervalues()
        except AttributeError:
            values = self.subs.copy().values()

        for s in values:
            if topic and topic == s.topic.name:
                yield s
            elif not topic:
                yield s

    def iter_topics(self, **reqkwargs):
        """Iterate over AmsTopic objects"""

        self.list_topics(**reqkwargs)

        try:
            values = self.topics.copy().itervalues()
        except AttributeError:
            values = self.topics.copy().values()

        for t in values:
            yield t

    def list_topics(self, **reqkwargs):
        """List the topics of a selected project

           Args:
               reqkwargs: keyword argument that will be passed to underlying
               python-requests library call
        """
        route = self.routes["topic_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.project)
        method = getattr(self, 'do_{0}'.format(route[0]))

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
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["topic_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, topic)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, "topic_get", **reqkwargs)

        if r['name'] not in self.topics:
            self._create_topic_obj(r)

        if retobj:
            return self.topics[r['name']]
        else:
            return r

    def publish(self, topic, msg, retry=0, retrysleep=60, retrybackoff=None, **reqkwargs):
        """Publish a message or list of messages to a selected topic.

           If enabled (retry > 0), multiple topic publishes will be tried in
           case of problems/glitches with the AMS service. retry* options are
           eventually passed to _retry_make_request()

           Args:
               topic (str): Topic name.
               msg (list): A list with one or more messages to send.
                           Each message is represented as AmsMessage object or python
                           dictionary with at least data or one attribute key defined.
           Kwargs:
               retry: int. Number of request retries before giving up. Default
                           is 0 meaning no further request retry will be made
                           after first unsuccesfull request.
               retrysleep: int. Static number of seconds to sleep before next
                           request attempt
               retrybackoff: int. Backoff factor to apply between each request
                             attempts
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
        url = route[1].format(self.endpoint, self.project, topic)
        method = getattr(self, 'do_{0}'.format(route[0]))

        return method(url, msg_body, "topic_publish", retry=retry,
                      retrysleep=retrysleep, retrybackoff=retrybackoff,
                      **reqkwargs)

    def list_subs(self, **reqkwargs):
        """Lists all subscriptions in a project with a GET request.

           Args:
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["sub_list"]
        # Compose url
        url = route[1].format(self.endpoint, self.project)
        method = getattr(self, 'do_{0}'.format(route[0]))

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
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["sub_get"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))

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

    def pull_sub(self, sub, num=1, return_immediately=False, retry=0,
                 retrysleep=60, retrybackoff=None, **reqkwargs):
        """This function consumes messages from a subscription in a project
           with a POST request.

           If enabled (retry > 0), multiple subscription pulls will be tried in
           case of problems/glitches with the AMS service. retry* options are
           eventually passed to _retry_make_request()

           Args:
               sub: str. The subscription name.
               num: int. The number of messages to pull.
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """

        wasmax = self.get_pullopt('maxMessages')
        wasretim = self.get_pullopt('returnImmediately')

        self.set_pullopt('maxMessages', num)
        self.set_pullopt('returnImmediately', str(return_immediately).lower())
        msg_body = json.dumps(self.pullopts)

        route = self.routes["sub_pull"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))
        r = method(url, msg_body, "sub_pull", retry=retry,
                   retrysleep=retrysleep, retrybackoff=retrybackoff,
                   **reqkwargs)
        msgs = r['receivedMessages']

        self.set_pullopt('maxMessages', wasmax)
        self.set_pullopt('returnImmediately', wasretim)

        return list(map(lambda m: (m['ackId'], AmsMessage(b64enc=False, **m['message'])), msgs))

    def ack_sub(self, sub, ids, **reqkwargs):
        """Acknownledgment of received messages

           Messages retrieved from a pull subscription can be acknowledged by
           sending message with an array of ackIDs. The service will retrieve
           the ackID corresponding to the highest message offset and will
           consider that message and all previous messages as acknowledged by
           the consumer.

           Args:
              sub: str. The subscription name.
              ids: list(str). A list of ids of the messages to acknowledge.
              reqkwargs: keyword argument that will be passed to underlying python-requests library call.
        """

        msg_body = json.dumps({"ackIds": ids})

        route = self.routes["sub_ack"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))
        method(url, msg_body, "sub_ack", **reqkwargs)

        return True

    def pullack_sub(self, sub, num=1, return_immediately=False, retry=0,
                    retrysleep=60, retrybackoff=None, **reqkwargs):
        """Pull messages from subscription and acknownledge them in one call.

           If enabled (retry > 0), multiple subscription pulls will be tried in
           case of problems/glitches with the AMS service. retry* options are
           eventually passed to _retry_make_request().

           If succesfull subscription pull immediately follows with failed
           acknownledgment (e.g. network hiccup just before acknowledgement of
           received messages), consume cycle will reset and start from
           beginning with new subscription pull. This ensures that ack deadline
           time window is moved to new start period, that is the time when the
           second pull was initiated.

           Args:
               sub: str. The subscription name.
               num: int. The number of messages to pull.
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        while True:
            try:
                ackIds = list()
                messages = list()

                for id, msg in self.pull_sub(sub, num,
                                             return_immediately=return_immediately,
                                             retry=retry,
                                             retrysleep=retrysleep,
                                             retrybackoff=retrybackoff,
                                             **reqkwargs):
                    ackIds.append(id)
                    messages.append(msg)

            except AmsException as e:
                raise e

            if messages and ackIds:
                try:
                    self.ack_sub(sub, ackIds, **reqkwargs)
                    break
                except AmsException as e:
                    log.warning('Continuing with sub_pull after sub_ack: {0}'.format(e))
                    pass
            else:
                break

        return messages

    def set_pullopt(self, key, value):
        """Function for setting pull options

           Args:
               key: str. The name of the pull option (ex. maxMessages, returnImmediately). Messaging specific
                    names are allowed.
               value: str or int. The name of the pull option (ex. maxMessages,
                      returnImmediately). Messaging specific names are allowed.
        """

        self.pullopts.update({key: str(value)})

    def get_pullopt(self, key):
        """Function for getting pull options

           Args:
               key: str. The name of the pull option (ex. maxMessages,
                    returnImmediately). Messaging specific names are allowed.

           Returns:
               str. The value of the pull option
        """
        return self.pullopts[key]

    def create_user(self, user, **reqkwargs):

        """
        This function creates a new user with a POST request

           Args:
               user: AmsUser. The user to be created.
               reqkwargs: keyword argument that will be passed to underlying
               python-requests library call.
           Return:
               object (AmsUser)
        """

        if not isinstance(user, AmsUser):
            raise ValueError("user has to be of type AmsUser")

        try:
            route = self.routes["user_create"]
            url = route[1].format(self.endpoint, user.name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, user.to_json(), "user_create", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def update_user(self, name,
                    first_name="",
                    last_name="",
                    description="",
                    organization="",
                    username="",
                    email="",
                    service_roles=None,
                    projects=None,
                    **reqkwargs):

        """
        Update the respective user using the provided username with a PUT request

        :param last_name: (str) the last name of the user
        :param first_name: (str) the first name of the user
        :param description: (str) user description
        :param organization: (str) user organisation
        :param username: (str) new username
        :param email: (str) the email the user
        :param service_roles: (str[]) new service roles
        :param projects: (AmsUserProject[]) new projects and roles
        :param name: (str) the username of the user to be updated
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUser) the ams user
        """

        body = {}

        if first_name != "":
            body["first_name"] = first_name

        if last_name != "":
            body["last_name"] = last_name

        if description != "":
            body["description"] = description

        if organization != "":
            body["organization"] = organization

        if username != "":
            body["name"] = username

        if email != "":
            body["email"] = email

        if len(service_roles) > 0:
            body["service_roles"] = service_roles

        if len(projects) > 0:
            body["projects"] = [{"project": x.project, "roles": x.roles} for x in projects]

        try:
            route = self.routes["user_update"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, json.dumps(body), "user_update", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def get_user(self, name, **reqkwargs):
        """
        Retrieves the respective user using the provided username with a GET request

        :param name: (str) the username of the user to be retrieved
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUser) the ams user
        """
        try:
            route = self.routes["user_get"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "user_get", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def get_user_by_token(self, token, **reqkwargs):
        """
        Retrieves the respective user using the provided token with a GET request

        :param token: (str) the token of the user to be retrieved
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUser) the ams user
        """
        try:
            route = self.routes["user_get_by_token"]
            url = route[1].format(self.endpoint, token)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "user_get_by_token", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def get_user_by_uuid(self, uuid, **reqkwargs):
        """
        Retrieves the respective user using the provided uuid with a GET request

        :param uuid: (str) the uuid of the user to be retrieved
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUser) the ams user
        """
        try:
            route = self.routes["user_get_by_uuid"]
            url = route[1].format(self.endpoint, uuid)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "user_get_by_uuid", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def get_user_profile(self, **reqkwargs):
        """
        Retrieves the respective user using the provided token in the ams object with a GET request
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUser) the ams user
        """
        try:
            route = self.routes["user_get_profile"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "user_get_profile", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def list_users(self, details=True, page_size=0, next_page_token="", **reqkwargs):
        """
        Retrieves the respective user using the provided token in the ams object with a GET request
        :param next_page_token: (str) next page token in case of paginated retrieval
        :param page_size: (int) size of each page
        :param details: (bool) whether to include project details per user
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUserPage) a page containing AmsUser objects and pagination details
        """
        try:
            url_params = {
                "details": details,
                "pageSize": page_size,
                "nextPageToken": next_page_token
            }
            route = self.routes["users_list"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            reqkwargs["params"] = url_params
            r = method(url, "users_list", **reqkwargs)
            return AmsUserPage(
                users=[AmsUser().load_from_dict(x) for x in r["users"]],
                total_size=r["totalSize"],
                next_page_token=r["nextPageToken"]
            )
        except AmsException as e:
            raise e

    def delete_user(self, name, **reqkwargs):
        """
        Deletes the respective user using the provided username with a DELETE request

        :param name: (str) the username of the user to be retrieved
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        """
        try:
            route = self.routes["user_delete"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "user_delete", **reqkwargs)
        except AmsException as e:
            raise e

    def refresh_user_token(self, name, **reqkwargs):
        """
        Refresh the token for the respective user using the provided username with a POST request

        :param name: (str) the username of the user to be retrieved
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
       :return: (AmsUser) the ams user
        """
        try:
            route = self.routes["user_refresh_token"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, None, "user_refresh_token", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def add_project_member(self, username, project=None, roles=None, **reqkwargs):
        """
        Assigns an existing user to the provided project with a POST request

        :param (str) project: the name of the project.If no
        project is supplied, the declared global project will be used instead
        :param (str) username: the name of user
        :param (str[]) roles: project roles for the user
        :param reqkwargs:  keyword argument that will be passed to underlying
                          python-requests library call.
        :return: (AmsUser) the assigned user object
        """

        if roles is None or not isinstance(roles, list):
            roles = []

        if project is None:
            project = self.project

        body = {
            "roles": roles
        }

        try:
            route = self.routes["project_add_member"]
            url = route[1].format(self.endpoint, project, username)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, json.dumps(body), "project_add_member", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def create_project_member(self, username, project=None, roles=None, email=None, **reqkwargs):

        """
        This function creates a new user with a POST request under the given project

        :param (str) project: the name of the project.If no
        project is supplied, the declared global project will be used instead
        :param (str) username: the name of the user
        :param (str) email: the email of the user
        :param (str[]) roles: project roles for the user

        :return: (AmsUser) the assigned user object
        """

        if roles is None or not isinstance(roles, list):
            roles = []

        if project is None:
            project = self.project

        user = AmsUser(
            projects=[AmsUserProject(project=project, roles=roles)]
        )

        if email is not None:
            user.email = email

        try:
            route = self.routes["project_create_member"]
            url = route[1].format(self.endpoint, project, username)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, user.to_json(), "project_create_member", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def get_project_member(self, username, project=None, **reqkwargs):
        """
        Retrieves the respective project member using the provided username with a GET request

        :param username: (str) the username of the user to be retrieved
        :param project: (str) the name of the project the user belongs to.If no
        project is supplied, the declared global project will be used instead
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        :return: (AmsUser) the ams user
        """
        try:
            if project is None:
                project = self.project

            route = self.routes["project_get_member"]
            url = route[1].format(self.endpoint, project, username)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "project_get_member", **reqkwargs)
            return AmsUser().load_from_dict(r)
        except AmsException as e:
            raise e

    def remove_project_member(self, username, project, **reqkwargs):
        """
        Removes an existing user from the provided project with a POST request

        :param username: (str) the name of user
        :param project: (Str) the name of the project
        :param reqkwargs:  keyword argument that will be passed to underlying
                          python-requests library call.
        """

        try:
            route = self.routes["project_remove_member"]
            url = route[1].format(self.endpoint, project, username)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, None, "project_remove_member", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def create_project(self, name, description, **reqkwargs):
        """
        Create a new project using the provided name and description with a POST request

        :param name: (str) the name of the project
        :param description: (str) the description of the project
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        """
        body = {
            "description": description
        }
        try:
            route = self.routes["project_create"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, json.dumps(body), "project_create", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def update_project(self, name, description="", updated_name="", **reqkwargs):
        """
        Create a new project using the provided name and description with a POST request

        :param name: (str) the name of the project
        :param description: (str) the description of the project
        :param updated_name: (str) updated name
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        """
        body = {}
        if description != "":
            body["description"] = description

        if updated_name != "":
            body["name"] = updated_name

        try:
            route = self.routes["project_update"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, json.dumps(body), "project_update", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def get_project(self, name, **reqkwargs):
        """
        Retrieve a project using the provided name with a GET request

        :param name: (str) the name of the project
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        """
        try:
            route = self.routes["project_get"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "project_get", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def delete_project(self, name, **reqkwargs):
        """
        Delete a project using the provided name with a DELETE request

        :param name: (str) the name of the project
        :param reqkwargs:  keyword arguments that will be passed to underlying
               python-requests library call.
        """
        try:
            route = self.routes["project_delete"]
            url = route[1].format(self.endpoint, name)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "project_delete", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def create_sub(self, sub, topic, ackdeadline=10, push_endpoint=None,
                   retry_policy_type='linear', retry_policy_period=300, retobj=False, **reqkwargs):
        """This function creates a new subscription in a project with a PUT request

           Args:
               sub: str. The subscription name.
               topic: str. The topic name.
               ackdeadline: int. It is a custom "ack" deadline (in seconds) in
                               the subscription. If your code doesn't
                               acknowledge the message in this time, the
                               message is sent again. If you don't specify
                               the deadline, the default is 10 seconds.
               push_endpoint: URL of remote endpoint that should receive
                              messages in push subscription mode
               retry_policy_type:
               retry_policy_period:
               retobj: Controls whether method should return AmsSubscription object
               reqkwargs: keyword argument that will be passed to underlying
               python-requests library call.
        """
        topic = self.get_topic(topic, retobj=True, **reqkwargs)

        msg_body = json.dumps({"topic": topic.fullname.strip('/'),
                               "ackDeadlineSeconds": ackdeadline})

        route = self.routes["sub_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, msg_body, "sub_create", **reqkwargs)

        if push_endpoint:
            ret = self.pushconfig_sub(sub, push_endpoint, retry_policy_type, retry_policy_period, **reqkwargs)
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
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["sub_delete"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, sub)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, "sub_delete", **reqkwargs)

        sub_fullname = "/projects/{0}/subscriptions/{1}".format(self.project, sub)
        if sub_fullname in self.subs:
            self._delete_sub_obj({'name': sub_fullname})

        return r

    def topic(self, topic, **reqkwargs):
        """Function create a topic in a project.

           It's wrapper around few methods defined in client class. Method will
           ensure that AmsTopic object is returned either by fetching existing
           one or creating a new one in case it doesn't exist.

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
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["topic_create"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, topic)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, '', "topic_create", **reqkwargs)

        if r['name'] not in self.topics:
            self._create_topic_obj(r)

        if retobj:
            return self.topics[r['name']]
        else:
            return r

    def delete_topic(self, topic, **reqkwargs):
        """This function deletes a topic in a project

           Args:
               topic: str. The topic name.
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
        """
        route = self.routes["topic_delete"]
        # Compose url
        url = route[1].format(self.endpoint, self.project, topic)
        method = getattr(self, 'do_{0}'.format(route[0]))

        r = method(url, "topic_delete", **reqkwargs)

        topic_fullname = "/projects/{0}/topics/{1}".format(self.project, topic)
        if topic_fullname in self.topics:
            self._delete_topic_obj({'name': topic_fullname})

        return r

    def status(self, **reqkwargs):
        """
        Retrieves the status of the service

        :param reqkwargs: keyword arguments that will be passed to underlying
               python-requests library call.
        """
        try:
            route = self.routes["api_status"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "api_status", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def metrics(self, **reqkwargs):
        """
        Retrieves the operational metrics of the service

        :param reqkwargs: keyword arguments that will be passed to underlying
               python-requests library call.
        """
        try:
            route = self.routes["api_metrics"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "api_metrics", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def version(self, **reqkwargs):
        """
        Retrieves the version information about the service

        :param reqkwargs: keyword arguments that will be passed to underlying
               python-requests library call.
        """
        try:
            route = self.routes["api_version"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            r = method(url, "api_version", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def va_metrics(self, projects=None, start_date=None, end_date=None, **reqkwargs):
        """
        Retrieves va report metrics for the given projects and the given time period
        :param projects: (str[]) filter based on the given projects
        :param start_date: (datetime.datetime time period starting date
        :param end_date: (datetime.datetime) time period end date
        :param reqkwargs: keyword arguments that will be passed to underlying
               python-requests library call.
        """

        url_params = {}

        if projects is None or not isinstance(projects, list):
            projects = []

        if start_date is not None and isinstance(start_date, datetime.datetime):
            url_params["start_date"] = start_date.strftime("%Y-%m-%d")

        if end_date is not None and isinstance(end_date, datetime.datetime):
            url_params["end_date"] = end_date.strftime("%Y-%m-%d")

        if len(projects) > 0:
            url_params["projects"] = ",".join(projects)

        try:
            route = self.routes["api_va_metrics"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            reqkwargs["params"] = url_params
            r = method(url, "api_va_metrics", **reqkwargs)
            return r
        except AmsException as e:
            raise e

    def usage_report(self, projects=None, start_date=None, end_date=None, **reqkwargs):
        """
        Retrieves va report metrics for the given projects and the given time period
        alongside the service's operational metrics.
        The api call will retrieve all projects that the requesting user is a project admin for.
        :param projects: (str[]) filter based on the given projects
        :param start_date: (datetime.datetime time period starting date
        :param end_date: (datetime.datetime) time period end date
        :param reqkwargs: keyword arguments that will be passed to underlying
               python-requests library call.
        """

        url_params = {}

        if projects is None or not isinstance(projects, list):
            projects = []

        if start_date is not None and isinstance(start_date, datetime.datetime):
            url_params["start_date"] = start_date.strftime("%Y-%m-%d")

        if end_date is not None and isinstance(end_date, datetime.datetime):
            url_params["end_date"] = end_date.strftime("%Y-%m-%d")

        if len(projects) > 0:
            url_params["projects"] = ",".join(projects)

        try:
            route = self.routes["api_usage_report"]
            url = route[1].format(self.endpoint)
            method = getattr(self, 'do_{0}'.format(route[0]))
            reqkwargs["params"] = url_params
            r = method(url, "api_usage_report", **reqkwargs)
            return r
        except AmsException as e:
            raise e
