from connexion.apps.flask_app import FlaskJSONEncoder
import six
import numpy as np

from pfeffernusse.models.base_model_ import Model


class JSONEncoder(FlaskJSONEncoder):
    include_nulls = False

    def default(self, o):
        if isinstance(o, Model):
            dikt = {}
            for attr, _ in six.iteritems(o.swagger_types):
                value = getattr(o, attr)
                if value is None and not self.include_nulls:
                    continue
                attr = o.attribute_map[attr]
                dikt[attr] = value
            return dikt
        # This should be in the model and the ISD dict that uses this should be
        # using models instead.
        elif isinstance(o, np.ndarray):
            lo = o.tolist()
            if len(lo) == 1:
                return lo[0]
            return lo

        return FlaskJSONEncoder.default(self, o)
