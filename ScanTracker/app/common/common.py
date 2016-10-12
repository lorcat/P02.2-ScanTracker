__author__ = 'Konstantin Glazyrin'

class Checker():
    def __init__(self):
        pass

    def check(self, value, vtype=None):
        res = False
        if vtype is None and value is not None:
            res = True
        elif value is not None and vtype is not None and isinstance(value, vtype):
            res = True
        return res

    def checkString(self, value):
        res = False
        if self.check(value, str) or self.check(value, unicode):
            res = True
        return res