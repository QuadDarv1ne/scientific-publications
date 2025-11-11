"""
Извлечение признаков с солнечных изображений.
"""

from typing import Dict, List

import numpy as np
from skimage import measure, morphology

from heliopy.imaging.image_processor import SolarImage


class FeatureExtractor:
    """Класс для извлечения признаков с изображений."""

    def __init__(self):
        """Инициализация экстрактора признаков."""
        pass

    def detect_active_regions(self, image: SolarImage, threshold: float = 0.5) -> List[Dict]:
        """
        Обнаружение активных областей на изображении.

        Parameters
        ----------
        image : SolarImage
            Входное изображение.
        threshold : float
            Порог для бинаризации.

        Returns
        -------
        list
            Список словарей с параметрами активных областей.
        """
        # Бинаризация
        binary = image.data > threshold * np.max(image.data)

        # Морфологическая обработка
        cleaned = morphology.remove_small_objects(binary, min_size=100)

        # Поиск связанных компонент
        labeled = measure.label(cleaned)
        regions = measure.regionprops(labeled, image.data)

        active_regions = []
        for region in regions:
            active_regions.append(
                {
                    "centroid": region.centroid,
                    "area": region.area,
                    "intensity_max": region.intensity_max,
                    "intensity_mean": region.intensity_mean,
                    "bbox": region.bbox,
                }
            )

        return active_regions

    def detect_sunspots(self, image: SolarImage, threshold: float = 0.3) -> List[Dict]:
        """
        Обнаружение солнечных пятен.

        Parameters
        ----------
        image : SolarImage
            Входное изображение.
        threshold : float
            Порог для обнаружения пятен.

        Returns
        -------
        list
            Список словарей с параметрами пятен.
        """
        # Инвертированное изображение для поиска темных областей
        inverted = 1.0 - (image.data / np.max(image.data))
        binary = inverted > threshold

        # Поиск связанных компонент
        labeled = measure.label(binary)
        regions = measure.regionprops(labeled, image.data)

        sunspots = []
        for region in regions:
            if region.area > 10:  # Минимальный размер пятна
                sunspots.append(
                    {
                        "centroid": region.centroid,
                        "area": region.area,
                        "intensity_min": region.intensity_min,
                        "intensity_mean": region.intensity_mean,
                        "bbox": region.bbox,
                    }
                )

        return sunspots

    def extract_statistics(self, image: SolarImage) -> Dict:
        """
        Извлечение статистических характеристик изображения.

        Parameters
        ----------
        image : SolarImage
            Входное изображение.

        Returns
        -------
        dict
            Словарь со статистическими характеристиками.
        """
        data = image.data
        return {
            "mean": np.mean(data),
            "std": np.std(data),
            "min": np.min(data),
            "max": np.max(data),
            "median": np.median(data),
            "percentile_25": np.percentile(data, 25),
            "percentile_75": np.percentile(data, 75),
        }
