"""
Загрузчик данных STEREO (Solar Terrestrial Relations Observatory).
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import numpy as np
from astropy.time import Time

from heliopy.data_sources.base_loader import BaseLoader


class STEREOLoader(BaseLoader):
    """Загрузчик данных STEREO."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика STEREO.

        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        super().__init__(cache_dir)

    def load_secchi(
        self, date: Union[str, datetime], spacecraft: str = "A", instrument: str = "EUVI", **kwargs
    ) -> "SolarImage":
        """
        Загрузка данных STEREO/SECCHI.

        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        spacecraft : str
            Космический аппарат ('A' или 'B').
        instrument : str
            Инструмент ('EUVI', 'COR1', 'COR2', 'HI1', 'HI2').
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        SolarImage
            Объект с данными изображения.
        """
        if spacecraft not in ["A", "B"]:
            raise ValueError("Космический аппарат должен быть 'A' или 'B'")
            
        if instrument not in ["EUVI", "COR1", "COR2", "HI1", "HI2"]:
            raise ValueError(f"Неподдерживаемый инструмент: {instrument}")

        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)

        # Ленивый импорт sunpy — чтобы импорт heliopy не падал, если sunpy не установлен.
        try:
            from sunpy.map import Map
            from sunpy.net import Fido
            from sunpy.net import attrs as a
        except ModuleNotFoundError:
            raise RuntimeError(
                "Для загрузки данных STEREO требуется пакет 'sunpy'. Установите его: pip install sunpy"
            )

        try:
            # Поиск данных через SunPy
            query = Fido.search(
                a.Time(time, time + 1 / 24),  # 1 час
                a.Detector("STEREO"),
                a.Instrument(instrument),
                a.Spacecraft(spacecraft)
            )

            if len(query) == 0:
                raise ValueError(f"Данные не найдены для {date}, космический аппарат {spacecraft}, инструмент {instrument}")

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
                wavelength=None,  # В реальной реализации можно извлечь длину волны из метаданных
                instrument=instrument,
                observatory=f"STEREO{spacecraft}",
            )

        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке данных STEREO/SECCHI: {e}")
