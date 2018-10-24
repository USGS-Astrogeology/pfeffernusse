from glob import glob
import os

import numpy as np
import pvl
import spiceypy as spice
from pfeffernusse import config

from pfeffernusse.drivers.base import LineScanner
from pfeffernusse.drivers.distortion import RadialDistortion

class MRO_CTX(LineScanner, RadialDistortion):

    @property
    def model_name(self):
        return "USGS_ASTRO_LINE_SCANNER_SENSOR_MODEL"

    @property
    def metakernel(self):
        metakernel_dir = config.mro
        mks = sorted(glob(os.path.join(metakernel_dir,'*.tm')))
        if not hasattr(self, '_metakernel'):
            for mk in mks:
                if str(self.start_time.year) in os.path.basename(mk):
                    self._metakernel = mk
        return self._metakernel

    @property
    def instrument_id(self):
        id_lookup = {
            'CONTEXT CAMERA':'MRO_CTX'
        }
        return id_lookup[self.label['INSTRUMENT_ID']]
    
    @property
    def spacecraft_name(self):
        name_lookup = {
            'MARS_RECONNAISSANCE_ORBITER': 'MRO'
        }
        return name_lookup[self.label['MISSION_NAME']]

    @property
    def reference_height(self):
        # TODO: This should be a reasonable #
        return 0, 100

    @property
    def image_samples(self):
        return self.label['LINE_SAMPLES']



