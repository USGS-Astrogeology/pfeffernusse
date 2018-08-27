import pvl
import zlib

import importlib
import os
from glob import glob

from flask import current_app as app

# dynamically load drivers
__all__ = [os.path.splitext(os.path.basename(d))[0] for d in glob(os.path.join(os.path.dirname(__file__), '*_driver.py'))]
__drivers__ = [importlib.import_module('.'+m, package='pfeffernusse.drivers') for m in __all__]

available_drivers = [os.path.basename(d).split('_')[0] for d in __all__]


def load(label):
    label = pvl.loads(label)
    for driver in __drivers__:
        try:
            try:
                return driver.get_isd(label)
            except Exception as e:
                print(e)
        except:
            pass
    raise Exception('No Such Driver for Label')
