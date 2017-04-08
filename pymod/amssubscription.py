class AmsSubscription(object):
    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/subscriptions/'.format(self.init.project))[1]

    def __init__(self, fullname, topic, pushconfig, ackdeadline, init):
        self.init = init
        self.fullname = fullname
        self.topic = self.init.topics[topic]
        self.pushconfig = pushconfig
        self.ackdeadline = ackdeadline
        self.name = self._build_name(self.fullname)

    def delete(self):
        self.init.delete_sub(self.name)

    def pull_sub(self, num=1, return_immediately=False, **reqkwargs):
        return self.init.pull_sub(self.name, num, return_immediately, **reqkwargs)

    def ack_sub(self, ids, **reqkwargs):
        return self.init.ack_sub(self.name, ids, **reqkwargs)
