"""
Mathematical utilities for heliophysics.
"""

from typing import Tuple, Union

import numpy as np


class MathUtils:
    """Mathematical utilities."""

    @staticmethod
    def spherical_to_cartesian(
        r: Union[float, np.ndarray], theta: Union[float, np.ndarray], phi: Union[float, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert spherical coordinates to Cartesian.

        Parameters
        ----------
        r : float or array
            Radial distance.
        theta : float or array
            Polar angle (from z-axis), in radians.
        phi : float or array
            Azimuthal angle, in radians.

        Returns
        -------
        x, y, z : arrays
            Cartesian coordinates.
        """
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z

    @staticmethod
    def cartesian_to_spherical(
        x: Union[float, np.ndarray], y: Union[float, np.ndarray], z: Union[float, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert Cartesian coordinates to spherical.

        Parameters
        ----------
        x, y, z : float or array
            Cartesian coordinates.

        Returns
        -------
        r, theta, phi : arrays
            Spherical coordinates (r, theta in radians, phi in radians).
        """
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / r)
        phi = np.arctan2(y, x)
        return r, theta, phi

    @staticmethod
    def angular_separation(
        lon1: Union[float, np.ndarray],
        lat1: Union[float, np.ndarray],
        lon2: Union[float, np.ndarray],
        lat2: Union[float, np.ndarray],
    ) -> Union[float, np.ndarray]:
        """
        Calculate angular distance between two points on a sphere.

        Parameters
        ----------
        lon1, lat1 : float or array
            Longitude and latitude of first point (in radians).
        lon2, lat2 : float or array
            Longitude and latitude of second point (in radians).

        Returns
        -------
        float or array
            Angular distance in radians.
        """
        # Формула гаверсинуса
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return c

    @staticmethod
    def great_circle_distance(
        lon1: Union[float, np.ndarray],
        lat1: Union[float, np.ndarray],
        lon2: Union[float, np.ndarray],
        lat2: Union[float, np.ndarray],
        radius: float = 1.0,
    ) -> Union[float, np.ndarray]:
        """
        Calculate great circle distance on a sphere.

        Parameters
        ----------
        lon1, lat1 : float or array
            Longitude and latitude of first point (in radians).
        lon2, lat2 : float or array
            Longitude and latitude of second point (in radians).
        radius : float
            Sphere radius.

        Returns
        -------
        float or array
            Great circle distance.
        """
        angular_sep = MathUtils.angular_separation(lon1, lat1, lon2, lat2)
        return radius * angular_sep
