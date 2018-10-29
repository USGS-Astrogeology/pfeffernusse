import pvl
import zlib

import importlib
import inspect
import os
from glob import glob

from flask import current_app as app

# dynamically load drivers
__all__ = [os.path.splitext(os.path.basename(d))[0] for d in glob(os.path.join(os.path.dirname(__file__), '*_driver.py'))]
__drivers__ = [importlib.import_module('.'+m, package='pfeffernusse.drivers') for m in __all__]

available_drivers = [os.path.basename(d).split('_')[0] for d in __all__]

def load(label):
    for driver in __drivers__:
        classes = inspect.getmembers(driver, inspect.isclass)
        for name, obj in classes:
            if name in ['Framer', 'LineScanner', 'TransverseDistortion', 'RadialDistortion']:
                continue
            #try:
            res = obj(label)
            if res.is_valid():
                app.logger.info('Successfully loaded {}'.format(name))
                with res as r:
                    resp = r.to_pfeffer_response()
                return resp
            #except: pass
    raise Exception('No Such Driver for Label')
