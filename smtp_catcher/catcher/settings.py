from configparser import ConfigParser


class Config:

    def __init__(self, file_name='settings.conf'):
        self._overwritten = {}
        self.cnf = ConfigParser()
        self.cnf.read(file_name)

    def __getitem__(self, k):
        k = k.lower()
        if k in self._overwritten:
            return self._overwritten[k]
        sec, key = k.split("_", 1)
        section = self.cnf[sec]
        return section[key]

    def __getattr__(self, k):
        if k == k.upper():
            return self[k]

    def __setitem__(self, k, v):
        self._overwritten[k.lower()] = v


def Setup(filename):
    global conf
    conf = Config(filename)
