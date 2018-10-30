from glob import glob
import os

import pvl
import spiceypy as spice
import numpy as np

from pfeffernusse import config
from pfeffernusse.drivers.base import Framer


class CassiniISS(Framer):
    id_lookup = {
        "ISSNA" : "CASSINI_ISS_NAC",
        "ISSWA" : "CASSINI_ISS_WAC"        
    }

    @property
    def metakernel(self):
        metakernel_dir = config.cassini
        mks = sorted(glob(os.path.join(metakernel_dir,'*.tm')))
        if not hasattr(self, '_metakernel'):
            for mk in mks:
                if str(self.start_time.year) in os.path.basename(mk):
                    self._metakernel = mk
        return self._metakernel

    @property
    def instrument_id(self):
        return self.id_lookup[self.label['INSTRUMENT_ID']]

    @property
    def focal_epsilon(self):
        return float(spice.gdpool('INS{}_FL_UNCERTAINTY'.format(self.ikid), 0, 1)[0])

    @property
    def spacecraft_name(self):
        return 'CASSINI'

    @property
    def focal2pixel_samples(self):
        # Microns to mm
        pixel_size = spice.gdpool('INS{}_PIXEL_SIZE'.format(self.ikid), 0, 1)[0] * 0.001
        return [0.0, 1/pixel_size, 0.0]

    @property
    def focal2pixel_lines(self):
        pixel_size = spice.gdpool('INS{}_PIXEL_SIZE'.format(self.ikid), 0, 1)[0] * 0.001
        return [0.0, 0.0, 1/pixel_size]

    @property
    def name_model(self):
        return "USGS_ASTRO_FRAME_SENSOR_MODEL"

    @property
    def reference_height(self):
        return 0, 100
    
    @property
    def _exposure_duration(self):
        return self.label['EXPOSURE_DURATION'] * 0.001  # Scale to seconds
