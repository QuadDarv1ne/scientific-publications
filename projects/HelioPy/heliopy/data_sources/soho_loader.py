"""
Загрузчик данных SOHO (Solar and Heliospheric Observatory).
"""

from typing import Optional, Union
from pathlib import Path
from datetime import datetime
from astropy.time import Time
from sunpy.net import Fido, attrs as a
from sunpy.map import Map
from heliopy.data_sources.base_loader import BaseLoader


class SOHOLoader(BaseLoader):
    """Загрузчик данных SOHO."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика SOHO.
        
        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        super().__init__(cache_dir)
    
    def load_lasco(self,
                   date: Union[str, datetime],
                   coronagraph: str = 'C2',
                   **kwargs) -> 'SolarImage':
        """
        Загрузка данных SOHO/LASCO.
        
        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        coronagraph : str
            Коронограф ('C2' или 'C3').
        **kwargs
            Дополнительные параметры.
        
        Returns
        -------
        SolarImage
            Объект с данными изображения.
        """
        if coronagraph not in ['C2', 'C3']:
            raise ValueError(f"Неподдерживаемый коронограф: {coronagraph}. Используйте 'C2' или 'C3'")
        
        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)
        
        try:
            query = Fido.search(
                a.Time(time, time + 1/24),
                a.Instrument('LASCO'),
                a.Detector(coronagraph)
            )
            
            if len(query) == 0:
                raise ValueError(f"Данные не найдены для {date} и коронографа {coronagraph}")
            
            files = Fido.fetch(query[0][0])
            
            if len(files) == 0:
                raise ValueError("Не удалось загрузить данные")
            
            sunpy_map = Map(files[0])
            
            from heliopy.imaging.image_processor import SolarImage
            return SolarImage(
                data=sunpy_map.data,
                header=sunpy_map.meta,
                time=sunpy_map.date,
                wavelength=None,
                instrument='LASCO',
                observatory='SOHO',
                coronagraph=coronagraph
            )
        
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке данных SOHO/LASCO: {e}")

