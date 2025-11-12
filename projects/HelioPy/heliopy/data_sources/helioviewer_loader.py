"""
Загрузчик данных Helioviewer.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import numpy as np
from astropy.time import Time

from heliopy.data_sources.base_loader import BaseLoader


class HelioviewerLoader(BaseLoader):
    """Загрузчик данных Helioviewer."""
    
    def load(self, *args, **kwargs):
        """Abstract method implementation."""
        pass

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика Helioviewer.

        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        super().__init__(cache_dir)
        self.base_url = "https://api.helioviewer.org/v2/"
        
    def load_image(
        self, date: Union[str, datetime], source_id: int = 14, **kwargs
    ) -> "SolarImage":
        """
        Загрузка изображения с Helioviewer.

        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        source_id : int
            ID источника данных (по умолчанию SDO/AIA 193Å).
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        SolarImage
            Объект с данными изображения.
        """
        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)

        # Ленивый импорт hvpy — чтобы импорт heliopy не падал, если hvpy не установлен.
        try:
            import hvpy
        except ModuleNotFoundError:
            raise RuntimeError(
                "Для загрузки данных Helioviewer требуется пакет 'hvpy'. Установите его: pip install hvpy"
            )

        try:
            # Получение изображения с Helioviewer API
            image_data = hvpy.getJP2Image(
                date=time.iso,
                sourceId=source_id
            )
            
            # Получение метаданных
            header_data = hvpy.getJP2Header(
                date=time.iso,
                sourceId=source_id
            )
            
            from heliopy.imaging.image_processor import SolarImage
            
            # Создание объекта SolarImage
            return SolarImage(
                data=np.array(image_data),  # В реальной реализации здесь будут данные изображения
                header=header_data,
                time=time,
                wavelength=self._get_wavelength_from_source(source_id),
                instrument=self._get_instrument_from_source(source_id),
                observatory=self._get_observatory_from_source(source_id),
            )
            
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке данных Helioviewer: {e}")
            
    def get_data_sources(self) -> dict:
        """
        Получение списка доступных источников данных.
        
        Returns
        -------
        dict
            Словарь с информацией об источниках данных.
        """
        try:
            import hvpy
            return hvpy.getDataSources()
        except ModuleNotFoundError:
            raise RuntimeError(
                "Для получения источников данных Helioviewer требуется пакет 'hvpy'. Установите его: pip install hvpy"
            )
            
    def _get_wavelength_from_source(self, source_id: int) -> Optional[float]:
        """Получение длины волны по ID источника."""
        # В реальной реализации здесь будет маппинг ID источников на длины волн
        wavelength_map = {
            14: 193.0,  # SDO/AIA 193Å
            13: 171.0,  # SDO/AIA 171Å
            15: 211.0,  # SDO/AIA 211Å
            16: 304.0,  # SDO/AIA 304Å
            17: 1600.0, # SDO/AIA 1600Å
            18: 1700.0, # SDO/AIA 1700Å
            19: 4500.0, # SDO/AIA 4500Å
        }
        return wavelength_map.get(source_id)
        
    def _get_instrument_from_source(self, source_id: int) -> str:
        """Получение названия инструмента по ID источника."""
        # В реальной реализации здесь будет маппинг ID источников на инструменты
        instrument_map = {
            14: "AIA",  # SDO/AIA 193Å
            13: "AIA",  # SDO/AIA 171Å
            15: "AIA",  # SDO/AIA 211Å
            16: "AIA",  # SDO/AIA 304Å
            17: "AIA",  # SDO/AIA 1600Å
            18: "AIA",  # SDO/AIA 1700Å
            19: "AIA",  # SDO/AIA 4500Å
        }
        return instrument_map.get(source_id, "Unknown")
        
    def _get_observatory_from_source(self, source_id: int) -> str:
        """Получение названия обсерватории по ID источника."""
        # В реальной реализации здесь будет маппинг ID источников на обсерватории
        observatory_map = {
            14: "SDO",  # SDO/AIA 193Å
            13: "SDO",  # SDO/AIA 171Å
            15: "SDO",  # SDO/AIA 211Å
            16: "SDO",  # SDO/AIA 304Å
            17: "SDO",  # SDO/AIA 1600Å
            18: "SDO",  # SDO/AIA 1700Å
            19: "SDO",  # SDO/AIA 4500Å
        }
        return observatory_map.get(source_id, "Unknown")