# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from pfeffernusse.models.base_model_ import Model
from pfeffernusse import util


class OpticalDistortionTransverse(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, x: List[float]=None, y: List[float]=None):  # noqa: E501
        """OpticalDistortionTransverse - a model defined in OpenAPI

        :param x: The x of this OpticalDistortionTransverse.  # noqa: E501
        :type x: List[float]
        :param y: The y of this OpticalDistortionTransverse.  # noqa: E501
        :type y: List[float]
        """
        self.openapi_types = {
            'x': List[float],
            'y': List[float]
        }

        self.attribute_map = {
            'x': 'x',
            'y': 'y'
        }

        self._x = x
        self._y = y

    @classmethod
    def from_dict(cls, dikt) -> 'OpticalDistortionTransverse':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The optical_distortion_transverse of this OpticalDistortionTransverse.  # noqa: E501
        :rtype: OpticalDistortionTransverse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def x(self) -> List[float]:
        """Gets the x of this OpticalDistortionTransverse.


        :return: The x of this OpticalDistortionTransverse.
        :rtype: List[float]
        """
        return self._x

    @x.setter
    def x(self, x: List[float]):
        """Sets the x of this OpticalDistortionTransverse.


        :param x: The x of this OpticalDistortionTransverse.
        :type x: List[float]
        """

        self._x = x

    @property
    def y(self) -> List[float]:
        """Gets the y of this OpticalDistortionTransverse.


        :return: The y of this OpticalDistortionTransverse.
        :rtype: List[float]
        """
        return self._y

    @y.setter
    def y(self, y: List[float]):
        """Sets the y of this OpticalDistortionTransverse.


        :param y: The y of this OpticalDistortionTransverse.
        :type y: List[float]
        """

        self._y = y
