class AmsTopic(object):
    def _build_name(self, fullname):
        return fullname.split('/projects/{0}/topics/'.format(self.init.project))[1]

    def __init__(self, fullname, init):
        self.fullname = fullname
        self.init = init
        self.name = self._build_name(self.fullname)
