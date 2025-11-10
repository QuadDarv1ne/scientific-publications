"""
Системы координат для гелиофизики.
"""

import numpy as np
from typing import Union, Tuple
from astropy import units as u
from astropy.coordinates import SkyCoord, HeliographicStonyhurst, HeliographicCarrington
from heliopy.utils.math_utils import MathUtils


class CoordinateSystem:
    """Класс для работы с системами координат."""
    
    @staticmethod
    def heliographic_to_cartesian(lon: Union[float, np.ndarray],
                                  lat: Union[float, np.ndarray],
                                  radius: Union[float, np.ndarray] = 1.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Преобразование гелиографических координат в декартовы.
        
        Parameters
        ----------
        lon : float или array
            Долгота в радианах.
        lat : float или array
            Широта в радианах.
        radius : float или array
            Радиус (по умолчанию 1.0).
        
        Returns
        -------
        x, y, z : arrays
            Декартовы координаты.
        """
        # В гелиографических координатах:
        # lat - это угол от экватора (широта)
        # lon - это долгота
        # Преобразуем в сферические координаты (theta от оси z, phi - азимут)
        theta = np.pi / 2 - lat  # Полярный угол от оси z
        phi = lon  # Азимутальный угол
        
        return MathUtils.spherical_to_cartesian(radius, theta, phi)
    
    @staticmethod
    def cartesian_to_heliographic(x: Union[float, np.ndarray],
                                  y: Union[float, np.ndarray],
                                  z: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Преобразование декартовых координат в гелиографические.
        
        Parameters
        ----------
        x, y, z : float или array
            Декартовы координаты.
        
        Returns
        -------
        lon, lat, radius : arrays
            Гелиографические координаты (lon, lat в радианах).
        """
        r, theta, phi = MathUtils.cartesian_to_spherical(x, y, z)
        lat = np.pi / 2 - theta  # Широта
        lon = phi  # Долгота
        return lon, lat, r
    
    @staticmethod
    def stonyhurst_to_carrington(lon_stonyhurst: Union[float, np.ndarray],
                                 lat_stonyhurst: Union[float, np.ndarray],
                                 time) -> Tuple[np.ndarray, np.ndarray]:
        """
        Преобразование из системы Stonyhurst в систему Carrington.
        
        Parameters
        ----------
        lon_stonyhurst : float или array
            Долгота Stonyhurst в радианах.
        lat_stonyhurst : float или array
            Широта Stonyhurst в радианах.
        time : Time
            Время для вычисления вращения.
        
        Returns
        -------
        lon_carrington, lat_carrington : arrays
            Координаты Carrington в радианах.
        """
        from heliopy.utils.time_utils import TimeUtils
        from astropy.time import Time
        
        time_obj = TimeUtils.parse_time(time)
        
        # Вычисление номера вращения Кэррингтона
        rotation_number = TimeUtils.carrington_rotation(time_obj)
        
        # Угол поворота между системами
        rotation_angle = (rotation_number - 1) * 360 * np.pi / 180
        
        # Преобразование долготы
        lon_carrington = lon_stonyhurst + rotation_angle
        lat_carrington = lat_stonyhurst
        
        return lon_carrington, lat_carrington
    
    @staticmethod
    def carrington_to_stonyhurst(lon_carrington: Union[float, np.ndarray],
                                 lat_carrington: Union[float, np.ndarray],
                                 time) -> Tuple[np.ndarray, np.ndarray]:
        """
        Преобразование из системы Carrington в систему Stonyhurst.
        
        Parameters
        ----------
        lon_carrington : float или array
            Долгота Carrington в радианах.
        lat_carrington : float или array
            Широта Carrington в радианах.
        time : Time
            Время для вычисления вращения.
        
        Returns
        -------
        lon_stonyhurst, lat_stonyhurst : arrays
            Координаты Stonyhurst в радианах.
        """
        from heliopy.utils.time_utils import TimeUtils
        
        time_obj = TimeUtils.parse_time(time)
        rotation_number = TimeUtils.carrington_rotation(time_obj)
        rotation_angle = (rotation_number - 1) * 360 * np.pi / 180
        
        lon_stonyhurst = lon_carrington - rotation_angle
        lat_stonyhurst = lat_carrington
        
        return lon_stonyhurst, lat_stonyhurst

