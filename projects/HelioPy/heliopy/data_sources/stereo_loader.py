"""
Загрузчик данных STEREO (Solar Terrestrial Relations Observatory).
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

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

        if isinstance(date, str):
            time = Time(date)
        else:
            time = Time(date)

        # В реальной реализации здесь будет загрузка данных STEREO
        # Для базовой версии создаем структуру
        from heliopy.imaging.image_processor import SolarImage

        # Заглушка
        return SolarImage(
            data=np.array([]),
            header={},
            time=time,
            wavelength=None,
            instrument=instrument,
            observatory=f"STEREO{spacecraft}",
        )
