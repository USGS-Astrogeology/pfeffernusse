from glob import glob
import os

from dateutil import parser
import pvl
import spiceypy as spice
import numpy as np

from pfeffernusse import config
from pfeffernusse.drivers.base import Base
from pfeffernusse.drivers.distortion import TransverseDistortion

from pfeffernusse.models.isd200 import ISD200

class Messenger(Base, TransverseDistortion):

    @property
    def metakernel(self):
        metakernel_dir = config.mdis
        mks = sorted(glob(os.path.join(metakernel_dir,'*.tm')))
        if not hasattr(self, '_metakernel'):
            for mk in mks:
                if str(self.start_time.year) in os.path.basename(mk):
                    self._metakernel = mk
        return self._metakernel

    @property
    def instrument_id(self):
        id_lookup = {
            'MDIS-NAC':'MSGR_MDIS_NAC',
            'MERCURY DUAL IMAGING SYSTEM NARROW ANGLE CAMERA':'MSGR_MDIS_NAC',
            'MERCURY DUAL IMAGING SYSTEM WIDE ANGLE CAMERA':'MSGR_MDIS_WAC'
        }
        return id_lookup[self.label['INSTRUMENT_ID']]

    @property
    def focal_length(self):
        """
        """
        coeffs = spice.gdpool('INS{}_FL_TEMP_COEFFS '.format(self.ikid), 0, 5)

        # reverse coeffs, mdis coeffs are listed a_0, a_1, a_2 ... a_n where
        # numpy wants them a_n, a_n-1, a_n-2 ... a_0
        f_t = np.poly1d(coeffs[::-1])

        # eval at the focal_plane_tempature
        return f_t(self.label['FOCAL_PLANE_TEMPERATURE'].value)

    @property
    def model_name(self):
        return "USGS_ASTRO_FRAME_SENSOR_MODEL"

    @property
    def reference_height(self):
        # TODO: This should be a reasonable #
        return 0

def get_isd(label):
    """
    TODO: This function (and all like it) needs to open with some robust method to make sure this is
          in fact an MDIS label.

    """
    m = Messenger(label)    
    return ISD200.from_dict(m.as_dict())
