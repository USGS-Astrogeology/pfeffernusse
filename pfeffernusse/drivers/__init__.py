import pvl
import zlib

import importlib
import inspect
import itertools
from itertools import chain
import os
from glob import glob

from abc import ABC

from flask import current_app as app

# dynamically load drivers
__all__ = [os.path.splitext(os.path.basename(d))[0] for d in glob(os.path.join(os.path.dirname(__file__), '*_driver.py'))]
__driver_modules__ = [importlib.import_module('.'+m, package='pfeffernusse.drivers') for m in __all__]

drivers = dict(chain.from_iterable(inspect.getmembers(dmod, lambda x: inspect.isclass(x) and "_driver" in x.__module__) for dmod in __driver_modules__))

def load(label):
    app.logger.info("Attempting drivers: {}".format(' '.join(drivers.keys())))
    for name, driver in drivers.items():
        try:
            res = driver(label)
            print(res.metakernel)
            if res.is_valid():
                app.logger.info('Successfully loaded {}'.format(name))
                with res as r:
                    resp = r.to_pfeffer_response()
                return resp
        except Exception as e:
            import traceback
            traceback.print_exc()
            app.logger.warning("{} failed: {}".format(name, e))
    raise Exception('No Such Driver for Label')
