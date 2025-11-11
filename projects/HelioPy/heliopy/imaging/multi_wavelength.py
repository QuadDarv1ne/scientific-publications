"""
Работа с мультиволновыми данными.
"""

from typing import Dict, List

import numpy as np

from heliopy.imaging.image_processor import SolarImage


class MultiWavelengthAnalyzer:
    """Класс для анализа мультиволновых данных."""

    def __init__(self):
        """Инициализация анализатора."""
        pass

    def create_composite(
        self,
        images: List[SolarImage],
        wavelengths: List[float],
        weights: Optional[List[float]] = None,
    ) -> SolarImage:
        """
        Создание композитного изображения из нескольких длин волн.

        Parameters
        ----------
        images : list
            Список изображений.
        wavelengths : list
            Список длин волн.
        weights : list, optional
            Веса для каждого изображения.

        Returns
        -------
        SolarImage
            Композитное изображение.
        """
        if len(images) != len(wavelengths):
            raise ValueError("Количество изображений должно совпадать с количеством длин волн")

        if weights is None:
            weights = [1.0] * len(images)

        # Нормализация изображений
        normalized = []
        for img in images:
            normalized.append((img.data - np.min(img.data)) / (np.max(img.data) - np.min(img.data)))

        # Взвешенная сумма
        composite = np.zeros_like(normalized[0])
        for img, weight in zip(normalized, weights):
            composite += weight * img

        composite = composite / np.sum(weights)

        # Создание нового изображения
        return SolarImage(
            data=composite,
            header=images[0].header.copy(),
            time=images[0].time,
            wavelength=None,
            instrument="Composite",
            observatory=images[0].observatory,
            wavelengths=wavelengths,
        )

    def extract_temperature_map(self, images: Dict[float, SolarImage]) -> np.ndarray:
        """
        Извлечение карты температуры из мультиволновых данных.

        Parameters
        ----------
        images : dict
            Словарь {длина_волны: изображение}.

        Returns
        -------
        array
            Карта температуры.
        """
        # Упрощенная реализация
        # В полной версии используется более сложный алгоритм
        # на основе соотношений интенсивностей на разных длинах волн

        # Заглушка
        if len(images) == 0:
            raise ValueError("Необходимо хотя бы одно изображение")

        first_image = list(images.values())[0]
        return np.ones_like(first_image.data) * 1e6  # Примерная температура в К
