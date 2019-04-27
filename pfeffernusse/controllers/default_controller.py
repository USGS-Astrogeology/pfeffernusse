import json

import connexion
import six

from pfeffernusse.models.data import Data  # noqa: E501
from pfeffernusse.models.isd200 import ISD200  # noqa: E501
from pfeffernusse.models.request_isd import RequestISD  # noqa: E501

from flask import current_app as app

import ale

@app.after_request
def apply_caching(response):
    """
    This sets the response for all responses. The response object
    can be used to parse on a specific type if necessary.
    """
    # Convert all http to https requests to prevent man-in-the-middle attackes
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # This should be a very strict policy to prevent any external injection - https://csp.withgoogle.com/docs/index.html
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    # Force the browser to render the type we indicate
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prohibit embedding our site in external iframes
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # If the post and response look like javascript, punt
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # We could set cookies here, but since we are not using cookies, I think we are okay.
    return response

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
    ale_string = ale.loads(request_isd.label)
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
    return util.get_metakernels(missions=mission, years=year, versions=version)


def metakernel_catalog():  # noqa: E501
    """Access Product Information

    Get Available Products and Related Metadata # noqa: E501


    :rtype: Data
    """
    return 'do some magic!'
