"""
Загрузчик данных SDO (Solar Dynamics Observatory).
"""

from typing import Optional, Union
from pathlib import Path
from datetime import datetime
import numpy as np
from astropy.time import Time
from sunpy.net import Fido, attrs as a
from sunpy.map import Map
from heliopy.data_sources.base_loader import BaseLoader


class SDOLoader(BaseLoader):
    """Загрузчик данных SDO."""
    
    # Поддерживаемые длины волн AIA
    AIA_WAVELENGTHS = [94, 131, 171, 193, 211, 304, 335]
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика SDO.
        
        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        super().__init__(cache_dir)
    
    def load_aia(self,
                 date: Union[str, datetime],
                 wavelength: int,
                 **kwargs) -> 'SolarImage':
        """
        Загрузка данных SDO/AIA.
        
        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        wavelength : int
            Длина волны в ангстремах.
        **kwargs
            Дополнительные параметры (например, time_range).
        
        Returns
        -------
        SolarImage
            Объект с данными изображения.
        """
        if wavelength not in self.AIA_WAVELENGTHS:
            raise ValueError(f"Неподдерживаемая длина волны: {wavelength} Å. "
                           f"Поддерживаемые: {self.AIA_WAVELENGTHS}")
        
        # Преобразование даты
        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)
        
        # Поиск данных через SunPy
        try:
            query = Fido.search(
                a.Time(time, time + 1/24),  # 1 час
                a.Instrument('AIA'),
                a.Wavelength(wavelength * a.angstrom)
            )
            
            if len(query) == 0:
                raise ValueError(f"Данные не найдены для {date} и длины волны {wavelength} Å")
            
            # Загрузка первого результата
            files = Fido.fetch(query[0][0])
            
            if len(files) == 0:
                raise ValueError("Не удалось загрузить данные")
            
            # Загрузка через SunPy Map
            sunpy_map = Map(files[0])
            
            # Создание объекта SolarImage
            from heliopy.imaging.image_processor import SolarImage
            return SolarImage(
                data=sunpy_map.data,
                header=sunpy_map.meta,
                time=sunpy_map.date,
                wavelength=wavelength,
                instrument='AIA',
                observatory='SDO'
            )
        
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке данных SDO/AIA: {e}")
    
    def load_hmi(self,
                 date: Union[str, datetime],
                 data_type: str = 'magnetogram',
                 **kwargs) -> 'SolarImage':
        """
        Загрузка данных SDO/HMI.
        
        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        data_type : str
            Тип данных ('magnetogram', 'continuum', 'dopplergram').
        **kwargs
            Дополнительные параметры.
        
        Returns
        -------
        SolarImage
            Объект с данными изображения.
        """
        if data_type not in ['magnetogram', 'continuum', 'dopplergram']:
            raise ValueError(f"Неподдерживаемый тип данных: {data_type}")
        
        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)
        
        try:
            # Определение типа данных для SunPy
            if data_type == 'magnetogram':
                product = 'hmi.M_720s'
            elif data_type == 'continuum':
                product = 'hmi.Ic_720s'
            elif data_type == 'dopplergram':
                product = 'hmi.V_720s'
            
            query = Fido.search(
                a.Time(time, time + 1/24),
                a.Instrument('HMI'),
                a.Physobs(data_type)
            )
            
            if len(query) == 0:
                raise ValueError(f"Данные не найдены для {date} и типа {data_type}")
            
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
                instrument='HMI',
                observatory='SDO',
                data_type=data_type
            )
        
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке данных SDO/HMI: {e}")

