from collections import namedtuple
from unittest import mock

import pytest

from pfeffernusse.drivers import mdis_driver, base, distortion
from pfeffernusse.drivers.mdis_driver import Messenger
from pfeffernusse.models.isd200 import ISD200


# 'Mock' the spice module where it is imported
from conftest import SimpleSpice

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
        d = m.to_dict()

        keys = ["model_name", "center_ephemeris_time", "dt_ephemeris", "focal2pixel_lines", "focal2pixel_samples",
                "focal_length", "focal_length_epsilon", "image_lines", "image_samples", "interpolation_method", "number_of_ephemerides",
                "odtx", "odty", "semimajor", "semiminor", "reference_height", "sensor_position",
                "sensor_orientation", "sensor_velocity", "detector_center", "starting_detector_line", "starting_detector_sample",
                "starting_ephemeris_time", "sun_position"]
        for k in keys:
            assert k in d.keys()  

def test_mdis_as_pfeffer_isd(mdislabel):
    with Messenger(mdislabel) as m:
        isd = m.to_pfeffer_response()
    # TODO: Need better tests here
    assert isinstance(isd, ISD200)

keys = ["model_name", "center_ephemeris_time", "dt_ephemeris", "focal2pixel_lines", "focal2pixel_samples",
    "focal_length_model", "image_lines", "image_samples", "interpolation_method", "number_of_ephemerides",
    "optical_distortion", "radii", "reference_height", "sensor_location",
    "sensor_orientation", "sensor_velocity", "detector_center", "starting_detector_line", "starting_detector_sample",
    "starting_ephemeris_time", "sun_position"]