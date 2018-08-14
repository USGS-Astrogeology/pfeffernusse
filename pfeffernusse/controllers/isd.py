import connexion
import six

from pfeffernusse.models.isd200 import ISD200  # noqa: E501
from pfeffernusse.models.request_isd import RequestISD  # noqa: E501
from pfeffernusse import util


def create_isd(request_isd=None):  # noqa: E501
    """Converts Image Labels to ISDs

    Adds an item to the system # noqa: E501

    :param request_isd: Inventory item to add
    :type request_isd: dict | bytes

    :rtype: ISD200
    """
    if connexion.request.is_json:
        request_isd = RequestISD.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
