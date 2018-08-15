# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from pfeffernusse.models.isd200 import ISD200  # noqa: E501
from pfeffernusse.models.request_isd import RequestISD  # noqa: E501
from pfeffernusse.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_create_isd(self):
        """Test case for create_isd

        Converts Image Labels to ISDs
        """
        label = RequestISD()
        response = self.client.open(
            '/v1/pds/',
            method='POST',
            data=json.dumps(label),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
