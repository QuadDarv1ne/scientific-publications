"""
Обработка солнечных изображений.
"""

from typing import Any, Dict, Optional

import numpy as np
from astropy.time import Time

from heliopy.core.data_processor import DataProcessor


class SolarImage:
    """Класс для представления солнечного изображения."""

    def __init__(
        self,
        data: np.ndarray,
        header: Dict[str, Any],
        time: Time,
        wavelength: Optional[float] = None,
        instrument: str = "",
        observatory: str = "",
        **kwargs,
    ):
        """
        Инициализация солнечного изображения.

        Parameters
        ----------
        data : array
            Данные изображения.
        header : dict
            Метаданные изображения.
        time : Time
            Время наблюдения.
        wavelength : float, optional
            Длина волны в ангстремах.
        instrument : str
            Название инструмента.
        observatory : str
            Название обсерватории.
        **kwargs
            Дополнительные параметры.
        """
        self.data = np.asarray(data)
        self.header = header
        self.time = Time(time)
        self.wavelength = wavelength
        self.instrument = instrument
        self.observatory = observatory
        self.metadata = kwargs

    @property
    def shape(self) -> tuple:
        """Форма данных изображения."""
        return self.data.shape

    def normalize(self, method: str = "minmax", **kwargs) -> "SolarImage":
        """
        Нормализация изображения.

        Parameters
        ----------
        method : str
            Метод нормализации.
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        SolarImage
            Новое нормализованное изображение.
        """
        normalized_data = DataProcessor.normalize(self.data, method=method, **kwargs)
        return SolarImage(
            data=normalized_data,
            header=self.header.copy(),
            time=self.time,
            wavelength=self.wavelength,
            instrument=self.instrument,
            observatory=self.observatory,
            **self.metadata,
        )

    def remove_background(self, method: str = "median", **kwargs) -> "SolarImage":
        """
        Удаление фона из изображения.

        Parameters
        ----------
        method : str
            Метод удаления фона.
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        SolarImage
            Новое изображение без фона.
        """
        processed_data = DataProcessor.remove_background(self.data, method=method, **kwargs)
        return SolarImage(
            data=processed_data,
            header=self.header.copy(),
            time=self.time,
            wavelength=self.wavelength,
            instrument=self.instrument,
            observatory=self.observatory,
            **self.metadata,
        )

    def denoise(self, method: str = "gaussian", **kwargs) -> "SolarImage":
        """
        Удаление шума из изображения.

        Parameters
        ----------
        method : str
            Метод удаления шума.
        **kwargs
            Дополнительные параметры.

        Returns
        -------
        SolarImage
            Новое изображение без шума.
        """
        processed_data = DataProcessor.denoise(self.data, method=method, **kwargs)
        return SolarImage(
            data=processed_data,
            header=self.header.copy(),
            time=self.time,
            wavelength=self.wavelength,
            instrument=self.instrument,
            observatory=self.observatory,
            **self.metadata,
        )


class ImageProcessor:
    """Класс для обработки солнечных изображений."""

    def __init__(self):
        """Инициализация процессора изображений."""
        self.processor = DataProcessor()

    def process(self, image: SolarImage, operations: list) -> SolarImage:
        """
        Применение последовательности операций к изображению.

        Parameters
        ----------
        image : SolarImage
            Входное изображение.
        operations : list
            Список операций для применения.

        Returns
        -------
        SolarImage
            Обработанное изображение.
        """
        result = image
        for operation in operations:
            if operation["type"] == "normalize":
                result = result.normalize(**operation.get("params", {}))
            elif operation["type"] == "remove_background":
                result = result.remove_background(**operation.get("params", {}))
            elif operation["type"] == "denoise":
                result = result.denoise(**operation.get("params", {}))
        return result
