"""
Обнаружение корональных выбросов массы (CME).
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from astropy.time import Time
from dataclasses import dataclass
from heliopy.imaging.image_processor import SolarImage
from astropy import units as u


@dataclass
class CME:
    """Класс для представления коронального выброса массы."""
    start_time: Time
    speed: float  # км/с
    acceleration: float  # км/с²
    direction: Dict[str, float]  # {'lon': float, 'lat': float}
    angular_width: float  # градусы
    mass: Optional[float] = None  # кг
    trajectory: Optional[List[Tuple[float, float, float]]] = None  # 3D траектория


class CMEDetector:
    """Класс для обнаружения и отслеживания CME."""
    
    def __init__(self):
        """Инициализация детектора CME."""
        pass
    
    def track_cme(self, lasco_data: List[SolarImage]) -> List[CME]:
        """
        Отслеживание CME в последовательности изображений LASCO.
        
        Parameters
        ----------
        lasco_data : list
            Список изображений LASCO.
        
        Returns
        -------
        list
            Список обнаруженных CME.
        """
        cme_events = []
        
        if len(lasco_data) < 2:
            return cme_events
        
        # Упрощенная реализация
        # В полной версии используется более сложный алгоритм
        # для отслеживания движения структур
        
        # Поиск ярких структур, движущихся наружу
        for i in range(len(lasco_data) - 1):
            img1 = lasco_data[i]
            img2 = lasco_data[i + 1]
            
            # Разностное изображение
            diff = img2.data - img1.data
            
            # Поиск ярких областей в разностном изображении
            threshold = np.percentile(diff, 95)
            bright_regions = diff > threshold
            
            if np.any(bright_regions):
                # Вычисление параметров CME
                cme = self._extract_cme_parameters(
                    img1, img2, bright_regions
                )
                
                if cme:
                    cme_events.append(cme)
        
        return cme_events
    
    def _extract_cme_parameters(self, img1: SolarImage, img2: SolarImage,
                               mask: np.ndarray) -> Optional[CME]:
        """
        Извлечение параметров CME из изображений.
        
        Parameters
        ----------
        img1, img2 : SolarImage
            Два последовательных изображения.
        mask : array
            Маска области CME.
        
        Returns
        -------
        CME или None
            Объект CME или None.
        """
        from skimage import measure
        
        # Нахождение центра масс
        labeled = measure.label(mask)
        regions = measure.regionprops(labeled)
        
        if len(regions) == 0:
            return None
        
        # Используем самую большую область
        largest_region = max(regions, key=lambda r: r.area)
        centroid = largest_region.centroid
        
        # Упрощенное вычисление скорости
        # В реальной версии используется более точный метод
        # с учетом масштаба изображения и времени между кадрами
        time_diff = (img2.time - img1.time).to(u.s).value
        if time_diff == 0:
            return None
        
        # Предполагаем, что движение происходит радиально
        # В реальной версии используется более сложная геометрия
        speed = 100.0  # км/с (заглушка)
        acceleration = 0.0  # км/с²
        
        # Направление (упрощенно)
        center = (img1.shape[1] // 2, img1.shape[0] // 2)
        direction_lon = np.arctan2(centroid[1] - center[1], 
                                  centroid[0] - center[0]) * 180 / np.pi
        direction_lat = 0.0  # Упрощение
        
        return CME(
            start_time=img1.time,
            speed=speed,
            acceleration=acceleration,
            direction={'lon': direction_lon, 'lat': direction_lat},
            angular_width=30.0  # градусы (заглушка)
        )

