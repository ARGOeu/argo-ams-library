class AmsSubscription(object):
    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/subscriptions/'.format(self.init.project))[1]

    def __init__(self, fullname, topic, pushconfig, ackdeadline, init):
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
        return self.init.delete_sub(self.name)

    def pushconfig(self, push_endpoint=None, retry_policy_type='linear', retry_policy_period=300, **reqkwargs):
        return self.init.pushconfig_sub(self.name, push_endpoint=push_endpoint,
                                        retry_policy_type=retry_policy_type,
                                        retry_policy_period=retry_policy_period,
                                        **reqkwargs)

    def pull(self, num=1, return_immediately=False, **reqkwargs):
        return self.init.pull_sub(self.name, num=num, return_immediately=return_immediately, **reqkwargs)

    def ack(self, ids, **reqkwargs):
        return self.init.ack_sub(self.name, ids, **reqkwargs)
