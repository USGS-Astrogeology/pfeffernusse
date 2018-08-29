import connexion
import six

from pfeffernusse.models.isd200 import ISD200  # noqa: E501
from pfeffernusse.models.request_isd import RequestISD  # noqa: E501
from pfeffernusse import util
import pfeffernusse as pf

def create_isd(label):  # noqa: E501
    """Converts Image Labels to ISDs

    Adds an item to the system # noqa: E501

    :param label:
    :type label: dict | bytes

    :rtype: ISD200
    """
    if connexion.request.is_json:
        label = RequestISD.from_dict(connexion.request.get_json())  # noqa: E501
    return pf.drivers.load(label.label)


def get_metakernel(mission, year, version):  # noqa: E501
    """Get a specific kernel

     # noqa: E501

    :param mission:
    :type mission: str
    :param year:
    :type year: str
    :param version:
    :type version: str

    :rtype: Data
    """
    return 'do some magic!'


def metakernel_catalog():  # noqa: E501
    """Access Product Information

    Get Available Products and Related Metadata # noqa: E501


    :rtype: Data
    """
    return 'do some magic!'
