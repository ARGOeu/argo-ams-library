class AmsTopic(object):
    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/topics/'.format(self.init.project))[1]

    def __init__(self, fullname, init):
        self.init = init
        self.fullname = fullname
        self.name = self._build_name(self.fullname)

    def delete(self):
        self.init.delete_topic(self.name)
