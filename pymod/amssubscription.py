class AmsSubscription(object):
    """Abstraction of AMS subscription

       Subscription represents stream of messages that can be pulled from AMS
       service or pushed to some receiver. Supported methods are wrappers
       around methods defined in client class with preconfigured
       subscription name.
    """
    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/subscriptions/'.format(self.init.project))[1]

    def __init__(self, fullname, topic, pushconfig, ackdeadline, init):
        self.acls = None
        self.init = init
        self.fullname = fullname
        self.topic = self.init.topics[topic]
        self.push_endpoint = ''
        self.retry_policy_type =  ''
        self.retry_policy_period = ''
        if pushconfig['pushEndpoint']:
            self.push_endpoint = pushconfig['pushEndpoint']
            self.retry_policy_type = pushconfig['retryPolicy']['type']
            self.retry_policy_period = pushconfig['retryPolicy']['period']
        self.ackdeadline = ackdeadline
        self.name = self._build_name(self.fullname)

    def delete(self):
        """Delete subscription"""

        return self.init.delete_sub(self.name)

    def pushconfig(self, push_endpoint=None, retry_policy_type='linear', retry_policy_period=300, **reqkwargs):
        """Configure Push mode parameters of subscription. When push_endpoint
           is defined, subscription will automatically start to send messages to it.

           Kwargs:
               push_endpoint (str): URL of remote endpoint that will receive messages
               retry_policy_type (str):
               retry_policy_period (int):
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.

        """

        return self.init.pushconfig_sub(self.name, push_endpoint=push_endpoint,
                                        retry_policy_type=retry_policy_type,
                                        retry_policy_period=retry_policy_period,
                                        **reqkwargs)

    def pull(self, num=1, return_immediately=False, **reqkwargs):
        """Pull messages from subscription

           Kwargs:
               num (int): Number of messages to pull
               return_immediately (boolean): If True and if stream of messages is empty,
                                             subscriber call will not block and wait for
                                             messages
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.
           Return:
               [(ackId, AmsMessage)]: List of tuples with ackId and AmsMessage instance
        """

        return self.init.pull_sub(self.name, num=num, return_immediately=return_immediately, **reqkwargs)

    def acl(self, users=None, **reqkwargs):
        """Set or get ACLs assigned to subscription

           Kwargs:
               users (list): If list of users is specified, give those user
                             access to subscription. Empty list will reset access permission.
               reqkwargs: keyword argument that will be passed to underlying
                          python-requests library call.

        """
        if users is None:
            return self.init.getacl_sub(self.name, **reqkwargs)
        else:
            return self.init.modifyacl_sub(self.name, users, **reqkwargs)

    def ack(self, ids, **reqkwargs):
        """Acknowledge receive of messages

           Kwargs:
               ids (list): A list of ackIds of the messages to acknowledge.
        """

        return self.init.ack_sub(self.name, ids, **reqkwargs)
