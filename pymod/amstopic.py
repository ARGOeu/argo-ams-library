class AmsTopic(object):
    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/topics/'.format(self.init.project))[1]

    def __init__(self, fullname, init):
        self.init = init
        self.fullname = fullname
        self.name = self._build_name(self.fullname)

    def delete(self):
        self.init.delete_topic(self.name)

    def subscription(self, sub, ackdeadline=10, **reqkwargs):
        return self.init.create_sub(sub, self.name, ackdeadline=ackdeadline, retobj=True, **reqkwargs)

    def iter_subs(self):
        for s in self.init.iter_subs(topic=self.name):
            yield s

    def publish(self, msg, **reqkwargs):
        return self.init.publish(self.name, msg, **reqkwargs)
