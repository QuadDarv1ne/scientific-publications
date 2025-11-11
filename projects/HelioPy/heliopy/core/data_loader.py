"""
Универсальный загрузчик данных.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from heliopy.data_sources.ace_loader import ACELoader
from heliopy.data_sources.goes_loader import GOESLoader
from heliopy.data_sources.sdo_loader import SDOLoader
from heliopy.data_sources.soho_loader import SOHOLoader
from heliopy.utils.config import get_config


class DataLoader:
    """Универсальный класс для загрузки данных из различных источников."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика данных.

        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        config = get_config()
        self.cache_dir = cache_dir or config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Инициализация загрузчиков для различных источников
        self.sdo_loader = SDOLoader(cache_dir=self.cache_dir)
        self.soho_loader = SOHOLoader(cache_dir=self.cache_dir)
        self.goes_loader = GOESLoader(cache_dir=self.cache_dir)
        self.ace_loader = ACELoader(cache_dir=self.cache_dir)

    def load_sdo_aia(self, date: Union[str, datetime], wavelength: int, **kwargs) -> "SolarImage":
        """
        Загрузка данных SDO/AIA.

        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        wavelength : int
            Длина волны в ангстремах (94, 131, 171, 193, 211, 304, 335).
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        SolarImage
            Объект с данными изображения.
        """
        return self.sdo_loader.load_aia(date, wavelength, **kwargs)

    def load_sdo_hmi(
        self, date: Union[str, datetime], data_type: str = "magnetogram", **kwargs
    ) -> "SolarImage":
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
        return self.sdo_loader.load_hmi(date, data_type, **kwargs)

    def load_soho_lasco(
        self, date: Union[str, datetime], coronagraph: str = "C2", **kwargs
    ) -> "SolarImage":
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
        return self.soho_loader.load_lasco(date, coronagraph, **kwargs)

    def load_goes(self, date: Union[str, datetime], **kwargs) -> "GOESData":
        """
        Загрузка данных GOES.

        Parameters
        ----------
        date : str или datetime
            Дата наблюдения.
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        GOESData
            Объект с данными GOES.
        """
        return self.goes_loader.load(date, **kwargs)

    def load_ace(self, date: Union[str, datetime], **kwargs) -> "ACEData":
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
        return self.ace_loader.load(date, **kwargs)


# Функции для удобного доступа (как в README)
def load_sdo_aia(date: Union[str, datetime], wavelength: int, **kwargs):
    """Удобная функция для загрузки данных SDO/AIA."""
    loader = DataLoader()
    return loader.load_sdo_aia(date, wavelength, **kwargs)


def load_soho_lasco(date: Union[str, datetime], coronagraph: str = "C2", **kwargs):
    """Удобная функция для загрузки данных SOHO/LASCO."""
    loader = DataLoader()
    return loader.load_soho_lasco(date, coronagraph, **kwargs)


def load_goes(date: Union[str, datetime], **kwargs):
    """Удобная функция для загрузки данных GOES."""
    loader = DataLoader()
    return loader.load_goes(date, **kwargs)
