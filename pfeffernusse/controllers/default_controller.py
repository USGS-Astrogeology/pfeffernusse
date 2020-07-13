import json

import connexion
import six

from pfeffernusse.models.data import Data  # noqa: E501
from pfeffernusse.models.isd200 import ISD200  # noqa: E501
from pfeffernusse.models.request_isd import RequestISD  # noqa: E501

from flask import current_app as app

import ale

def create_isd():  # noqa: E501
    """Converts Image Labels to ISDs

    Adds an item to the system # noqa: E501

    :param request_isd:
    :type request_isd: dict | bytes

    :rtype: ISD200
    """
    if connexion.request.is_json:
        request_isd = RequestISD.from_dict(connexion.request.get_json())  # noqa: E501

    app.logger.info("Post Request: {}".format(request_isd))

    try:
        ale_string = ale.loads(request_isd.label)
    except Exception as e:
        app.logger.info(f"Unable to generate isd from label with error: {e}")
        ale_string = '{}'

    return json.loads(ale_string)

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
    if connexion.request.is_json:
        request_isd = RequestISD.from_dict(connexion.request.get_json())  # noqa: E501
    try:
        metakernel = ale.util.get_metakernels(missions=mission, years=year, versions=version)
    except Exception as e:
        app.logger.info(f"Unable to retrieve metakernel for {mission}, " +
                        f"{year}, {version}. Failed from ALE with: {e}")
        metakernel = ""
    return metakernel


def metakernel_catalog():  # noqa: E501
    """Access Product Information

    Get Available Products and Related Metadata # noqa: E501


    :rtype: Data
    """
    return 'do some magic!'
