"""
Реконструкция магнитных полей.
"""

import numpy as np

from heliopy.imaging.image_processor import SolarImage


class FieldReconstructor:
    """Класс для реконструкции магнитных полей."""

    def __init__(self):
        """Инициализация реконструктора."""
        pass

    def reconstruct_field(self, magnetogram: SolarImage, method: str = "potential") -> np.ndarray:
        """
        Реконструкция магнитного поля.

        Parameters
        ----------
        magnetogram : SolarImage
            Магнитограмма.
        method : str
            Метод реконструкции ('potential', 'nlff').

        Returns
        -------
        array
            Реконструированное поле.
        """
        # Заглушка - в полной версии реализуется полная реконструкция
        return np.zeros_like(magnetogram.data)
