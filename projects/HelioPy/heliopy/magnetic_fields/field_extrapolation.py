"""
Экстраполяция магнитных полей в корону.
"""

import numpy as np

from heliopy.imaging.image_processor import SolarImage


class FieldExtrapolator:
    """Класс для экстраполяции полей."""

    def __init__(self):
        """Инициализация экстраполятора."""
        pass

    def extrapolate(self, magnetogram: SolarImage, height: float) -> np.ndarray:
        """
        Экстраполяция поля на заданную высоту.

        Parameters
        ----------
        magnetogram : SolarImage
            Магнитограмма.
        height : float
            Высота в солнечных радиусах.

        Returns
        -------
        array
            Экстраполированное поле.
        """
        # Заглушка
        return np.zeros_like(magnetogram.data)
