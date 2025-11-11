"""
Coordinate systems for heliophysics.
"""

from typing import Tuple, Union

import numpy as np

# Some versions of astropy may not provide specific coordinate system names
# (HeliographicStonyhurst/HeliographicCarrington). Import is performed in a protected
# mode to avoid errors when importing the package in environments with a different astropy version.
try:
    from astropy.coordinates import SkyCoord  # type: ignore
except Exception:
    SkyCoord = None
from heliopy.utils.math_utils import MathUtils


class CoordinateSystem:
    """Class for working with coordinate systems."""

    @staticmethod
    def heliographic_to_cartesian(
        lon: Union[float, np.ndarray],
        lat: Union[float, np.ndarray],
        radius: Union[float, np.ndarray] = 1.0,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert heliographic coordinates to Cartesian.

        Parameters
        ----------
        lon : float or array
            Longitude in radians.
        lat : float or array
            Latitude in radians.
        radius : float or array
            Radius (default 1.0).

        Returns
        -------
        x, y, z : arrays
            Cartesian coordinates.
        """
        # In heliographic coordinates:
        # lat - is the angle from the equator (latitude)
        # lon - is the longitude
        # Convert to spherical coordinates (theta from z-axis, phi - azimuth)
        theta = np.pi / 2 - lat  # Polar angle from z-axis
        phi = lon  # Azimuthal angle

        return MathUtils.spherical_to_cartesian(radius, theta, phi)

    @staticmethod
    def cartesian_to_heliographic(
        x: Union[float, np.ndarray], y: Union[float, np.ndarray], z: Union[float, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert Cartesian coordinates to heliographic.

        Parameters
        ----------
        x, y, z : float or array
            Cartesian coordinates.

        Returns
        -------
        lon, lat, radius : arrays
            Heliographic coordinates (lon, lat in radians).
        """
        r, theta, phi = MathUtils.cartesian_to_spherical(x, y, z)
        lat = np.pi / 2 - theta  # Latitude
        lon = phi  # Longitude
        return lon, lat, r

    @staticmethod
    def stonyhurst_to_carrington(
        lon_stonyhurst: Union[float, np.ndarray], lat_stonyhurst: Union[float, np.ndarray], time
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert from Stonyhurst system to Carrington system.

        Parameters
        ----------
        lon_stonyhurst : float or array
            Stonyhurst longitude in radians.
        lat_stonyhurst : float or array
            Stonyhurst latitude in radians.
        time : Time
            Time for rotation calculation.

        Returns
        -------
        lon_carrington, lat_carrington : arrays
            Carrington coordinates in radians.
        """

        from heliopy.utils.time_utils import TimeUtils

        time_obj = TimeUtils.parse_time(time)

        # Calculate Carrington rotation number
        rotation_number = TimeUtils.carrington_rotation(time_obj)

        # Rotation angle between systems
        rotation_angle = (rotation_number - 1) * 360 * np.pi / 180

        # Longitude transformation
        lon_carrington = lon_stonyhurst + rotation_angle
        lat_carrington = lat_stonyhurst

        return np.asarray(lon_carrington), np.asarray(lat_carrington)

    @staticmethod
    def carrington_to_stonyhurst(
        lon_carrington: Union[float, np.ndarray], lat_carrington: Union[float, np.ndarray], time
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert from Carrington system to Stonyhurst system.

        Parameters
        ----------
        lon_carrington : float or array
            Carrington longitude in radians.
        lat_carrington : float or array
            Carrington latitude in radians.
        time : Time
            Time for rotation calculation.

        Returns
        -------
        lon_stonyhurst, lat_stonyhurst : arrays
            Stonyhurst coordinates in radians.
        """
        from heliopy.utils.time_utils import TimeUtils

        time_obj = TimeUtils.parse_time(time)
        rotation_number = TimeUtils.carrington_rotation(time_obj)
        rotation_angle = (rotation_number - 1) * 360 * np.pi / 180

        lon_stonyhurst = lon_carrington - rotation_angle
        lat_stonyhurst = lat_carrington

        return np.asarray(lon_stonyhurst), np.asarray(lat_stonyhurst)
