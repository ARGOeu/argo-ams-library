class AmsTopic(object):
    def _build_name(self, fullname):
        try:
            t = fullname.split('/projects/{0}/topics/'.format(self.init.project))[1]
        except Exception:
            t = fullname.split('/project/{0}/topics/'.format(self.init.project))[1]
        return t

    def __init__(self, fullname, init):
        self.init = init
        self.fullname = fullname
        self.name = self._build_name(self.fullname)
