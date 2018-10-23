import numpy as np


class SimpleSpice():
    def scs2e(self, x, y):
        return y
    def bods2c(self, x):
        return -12345
    def gdpool(self, key, x, length):
        return np.ones(length).tolist()
    def bodvrd(self, key, x, length):
        return (3, np.ones(length,).tolist())
    def spkpos(self, *args):
        return (np.ones(3).tolist(), None)
    def spkezr(self, *args):
        return (np.ones(6).tolist(), None)
    def furnsh(self, *args):
        return
    def unload(self, *args):
        return
    def pxform(self, *args):
        return
    def m2q(self, *args):
        return [1,2,3,4]