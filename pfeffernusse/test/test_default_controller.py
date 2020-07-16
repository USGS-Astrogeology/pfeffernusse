# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from pfeffernusse.models.data import Data  # noqa: E501
from pfeffernusse.models.isd200 import ISD200  # noqa: E501
from pfeffernusse.models.request_isd import RequestISD  # noqa: E501
from pfeffernusse.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """
    DefaultController integration test stubs
    """

    def test_create_isd(self):
        """
        Test case for create_isd

        Converts Image Labels to ISDs
        """
        request_isd = RequestISD()
        response = self.client.open(
            '/v1/pds/',
            method='POST',
            data=json.dumps(request_isd),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_metakernel(self):
        """Test case for get_metakernel

        Get a specific kernel
        """
        query_string = [('mission', 'mission_example'),
                        ('year', 'year_example'),
                        ('version', 'latest')]
        response = self.client.open(
            '/v1/metakernels/',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_metakernel_catalog(self):
        """Test case for metakernel_catalog

        Access Product Information
        """
        response = self.client.open(
            '/v1/metakernels/catalog/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
