from collections import namedtuple
from unittest import mock

import numpy as np
import pytest

from pfeffernusse.drivers import mdis_driver, base, distortion
from pfeffernusse.drivers.mdis_driver import Messenger, get_isd

class SimpleSpice():
    def scs2e(self, x, y):
        return y
    def bods2c(self, x):
        return x
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
             'FOCAL_PLANE_TEMPERATURE':Pvllike(0, 'deg'),
             'START_TIME':'2005-01-01T12:00:00.0'}
    return label

def test_mdis_creation(mdislabel):
    with Messenger(mdislabel) as m:
        d = m.as_dict()

        keys = ["model_name", "center_ephemeris_time", "dt_ephemeris", "focal2pixel_lines", "focal2pixel_samples",
                "focal_length", "focal_length_epsilon", "image_lines", "image_samples", "interpolation_method", "number_of_ephemerides",
                "odtx", "odty", "semimajor", "semiminor", "reference_height", "sensor_position",
                "sensor_orientation", "sensor_velocity", "detector_center", "starting_detector_line", "starting_detector_sample",
                "starting_ephemeris_time", "sun_position"]
        for k in keys:
            assert k in d.keys()  

def test_mdis_as_pfeffer_isd(mdislabel):
    isd = get_isd(mdislabel)

keys = ["model_name", "center_ephemeris_time", "dt_ephemeris", "focal2pixel_lines", "focal2pixel_samples",
    "focal_length_model", "image_lines", "image_samples", "interpolation_method", "number_of_ephemerides",
    "optical_distortion", "radii", "reference_height", "sensor_location",
    "sensor_orientation", "sensor_velocity", "detector_center", "starting_detector_line", "starting_detector_sample",
    "starting_ephemeris_time", "sun_position"]