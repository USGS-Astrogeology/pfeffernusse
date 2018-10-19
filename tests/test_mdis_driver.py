from collections import namedtuple
from unittest import mock

import numpy as np
import pytest

from pfeffernusse.drivers import mdis_driver, base, distortion
from pfeffernusse.drivers.mdis_driver import Messenger

class SimpleSpice():
    def scs2e(self, x, y):
        return y
    def bods2c(self, x):
        return x
    def gdpool(self, key, x, length):
        return np.ones(length)
    def bodvrd(self, key, x, length):
        return (3, np.ones(length,))
    def spkpos(self, *args):
        return (np.ones(3), None)
    def spkezr(self, *args):
        return (np.ones(6), None)

# 'Mock' the spice module where it is imported
simplespice = SimpleSpice()
base.spice = simplespice
mdis_driver.spice = simplespice
distortion.spice = simplespice

@pytest.fixture
def mdislabel():
    Pvllike = namedtuple('Pvllike', ['value', 'unit'])
    label = {'LINES':10,
             'SAMPLES':10,
             'TARGET_NAME':'mercury',
             'SPACECRAFT_CLOCK_START_COUNT':0,
             'EXPOSURE_DURATION':Pvllike(10, 'm'),
             'SPACECRAFT_CLOCK_STOP_COUNT':10,
             'MISSION_NAME':'messenger', 
             'INSTRUMENT_ID': 'MDIS-NAC',
             'FOCAL_PLANE_TEMPERATURE':Pvllike(0, 'deg')}
    return label

def test_mdis_creation(mdislabel):
    m = Messenger(mdislabel)
    d = m.as_dict()
    assert False    