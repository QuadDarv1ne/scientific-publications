"""
Анализ геомагнитных бурь.
"""

from typing import Dict, List

import numpy as np
import pandas as pd


class GeomagneticStormAnalyzer:
    """Класс для анализа геомагнитных бурь."""

    # Пороги для классификации бурь по Dst
    STORM_THRESHOLDS = {
        "minor": -50,  # нТл
        "moderate": -100,
        "strong": -200,
        "severe": -350,
    }

    def __init__(self):
        """Инициализация анализатора."""
        pass

    def detect_storms(self, dst_data: pd.DataFrame) -> List[Dict]:
        """
        Обнаружение геомагнитных бурь в данных Dst.

        Parameters
        ----------
        dst_data : DataFrame
            DataFrame с колонками 'time' и 'dst'.

        Returns
        -------
        list
            Список словарей с параметрами бурь.
        """
        storms = []

        if "dst" not in dst_data.columns:
            return storms

        dst_values = dst_data["dst"].values
        time_values = dst_data["time"].values if "time" in dst_data.columns else None

        # Порог для начала бури
        threshold = -50  # нТл

        in_storm = False
        storm_start_idx = None
        storm_min_dst = 0

        for i, dst in enumerate(dst_values):
            if dst < threshold and not in_storm:
                # Начало бури
                in_storm = True
                storm_start_idx = i
                storm_min_dst = dst
            elif dst < threshold and in_storm:
                # Продолжение бури
                if dst < storm_min_dst:
                    storm_min_dst = dst
            elif dst >= threshold and in_storm:
                # Конец бури
                in_storm = False

                storm = {
                    "start_time": time_values[storm_start_idx] if time_values is not None else None,
                    "min_dst": storm_min_dst,
                    "classification": self._classify_storm(storm_min_dst),
                    "duration_hours": (i - storm_start_idx) * 1.0,  # Предполагаем 1 час на точку
                }
                storms.append(storm)

        return storms

    def _classify_storm(self, min_dst: float) -> str:
        """
        Классификация бури по минимальному Dst.

        Parameters
        ----------
        min_dst : float
            Минимальное значение Dst.

        Returns
        -------
        str
            Классификация бури.
        """
        if min_dst < self.STORM_THRESHOLDS["severe"]:
            return "severe"
        elif min_dst < self.STORM_THRESHOLDS["strong"]:
            return "strong"
        elif min_dst < self.STORM_THRESHOLDS["moderate"]:
            return "moderate"
        elif min_dst < self.STORM_THRESHOLDS["minor"]:
            return "minor"
        else:
            return "none"

    def calculate_kp_index(self, magnetic_field_data: pd.DataFrame) -> np.ndarray:
        """
        Расчет индекса Kp из данных магнитного поля.

        Parameters
        ----------
        magnetic_field_data : DataFrame
            DataFrame с данными магнитного поля.

        Returns
        -------
        array
            Массив значений Kp.
        """
        # Упрощенная реализация
        # В реальной версии используется более сложный алгоритм
        # на основе данных с нескольких обсерваторий

        if "Bx" not in magnetic_field_data.columns or "By" not in magnetic_field_data.columns:
            return np.array([])

        # Упрощенный расчет на основе компонент магнитного поля
        B_total = np.sqrt(magnetic_field_data["Bx"] ** 2 + magnetic_field_data["By"] ** 2)

        # Преобразование в Kp (упрощенное)
        kp = (B_total - 20) / 10
        kp = np.clip(kp, 0, 9)

        return kp
