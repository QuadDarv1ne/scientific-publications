"""
Математические утилиты для гелиофизики.
"""

import numpy as np
from typing import Union, Tuple
from astropy import units as u


class MathUtils:
    """Математические утилиты."""
    
    @staticmethod
    def spherical_to_cartesian(r: Union[float, np.ndarray],
                               theta: Union[float, np.ndarray],
                               phi: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Преобразование сферических координат в декартовы.
        
        Parameters
        ----------
        r : float или array
            Радиальное расстояние.
        theta : float или array
            Полярный угол (от оси z), в радианах.
        phi : float или array
            Азимутальный угол, в радианах.
        
        Returns
        -------
        x, y, z : arrays
            Декартовы координаты.
        """
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z
    
    @staticmethod
    def cartesian_to_spherical(x: Union[float, np.ndarray],
                               y: Union[float, np.ndarray],
                               z: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Преобразование декартовых координат в сферические.
        
        Parameters
        ----------
        x, y, z : float или array
            Декартовы координаты.
        
        Returns
        -------
        r, theta, phi : arrays
            Сферические координаты (r, theta в радианах, phi в радианах).
        """
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / r)
        phi = np.arctan2(y, x)
        return r, theta, phi
    
    @staticmethod
    def angular_separation(lon1: Union[float, np.ndarray],
                          lat1: Union[float, np.ndarray],
                          lon2: Union[float, np.ndarray],
                          lat2: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Вычисление углового расстояния между двумя точками на сфере.
        
        Parameters
        ----------
        lon1, lat1 : float или array
            Долгота и широта первой точки (в радианах).
        lon2, lat2 : float или array
            Долгота и широта второй точки (в радианах).
        
        Returns
        -------
        float или array
            Угловое расстояние в радианах.
        """
        # Формула гаверсинуса
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return c
    
    @staticmethod
    def great_circle_distance(lon1: Union[float, np.ndarray],
                             lat1: Union[float, np.ndarray],
                             lon2: Union[float, np.ndarray],
                             lat2: Union[float, np.ndarray],
                             radius: float = 1.0) -> Union[float, np.ndarray]:
        """
        Вычисление расстояния по большому кругу на сфере.
        
        Parameters
        ----------
        lon1, lat1 : float или array
            Долгота и широта первой точки (в радианах).
        lon2, lat2 : float или array
            Долгота и широта второй точки (в радианах).
        radius : float
            Радиус сферы.
        
        Returns
        -------
        float или array
            Расстояние по большому кругу.
        """
        angular_sep = MathUtils.angular_separation(lon1, lat1, lon2, lat2)
        return radius * angular_sep

