"""
Загрузчик данных ACE (Advanced Composition Explorer).
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import numpy as np
from astropy.time import Time

from heliopy.data_sources.base_loader import BaseLoader


class ACELoader(BaseLoader):
    """Загрузчик данных ACE."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика ACE.

        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        super().__init__(cache_dir)
        self.base_url = "https://www.swpc.noaa.gov/products/ace-real-time-solar-wind"

    def load(self, date: Union[str, datetime], **kwargs) -> "ACEData":
        """
        Загрузка данных ACE.

        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        ACEData
            Объект с данными ACE.
        """
        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)

        # В реальной реализации здесь будет загрузка данных ACE
        # Для базовой версии создаем структуру данных
        from heliopy.space_weather.forecast_models import ACEData

        # Заглушка - в полной версии здесь будет реальная загрузка
        data = {
            "time": time,
            "proton_density": np.array([]),
            "proton_speed": np.array([]),
            "proton_temperature": np.array([]),
            "magnetic_field": np.array([]),
        }

        return ACEData(**data)
