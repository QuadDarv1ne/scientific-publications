"""
Статистические утилиты для анализа данных.
"""

from typing import Tuple

import numpy as np
from scipy import stats


class StatsUtils:
    """Статистические утилиты."""

    @staticmethod
    def robust_statistics(data: np.ndarray) -> dict:
        """
        Вычисление устойчивых статистических характеристик.

        Parameters
        ----------
        data : array
            Массив данных.

        Returns
        -------
        dict
            Словарь со статистическими характеристиками.
        """
        median = np.median(data)
        mad = np.median(np.abs(data - median))  # Median Absolute Deviation
        q25, q75 = np.percentile(data, [25, 75])
        iqr = q75 - q25

        return {
            "median": median,
            "mad": mad,
            "q25": q25,
            "q75": q75,
            "iqr": iqr,
        }

    @staticmethod
    def remove_outliers(data: np.ndarray, method: str = "iqr", factor: float = 1.5) -> np.ndarray:
        """
        Удаление выбросов из данных.

        Parameters
        ----------
        data : array
            Массив данных.
        method : str
            Метод удаления выбросов ('iqr' или 'zscore').
        factor : float
            Фактор для определения выбросов.

        Returns
        -------
        array
            Массив данных без выбросов.
        """
        if method == "iqr":
            q25, q75 = np.percentile(data, [25, 75])
            iqr = q75 - q25
            lower_bound = q25 - factor * iqr
            upper_bound = q75 + factor * iqr
            mask = (data >= lower_bound) & (data <= upper_bound)
        elif method == "zscore":
            z_scores = np.abs(stats.zscore(data))
            mask = z_scores < factor
        else:
            raise ValueError(f"Неизвестный метод: {method}")

        return data[mask]

    @staticmethod
    def correlation_coefficient(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
        """
        Вычисление коэффициента корреляции Пирсона.

        Parameters
        ----------
        x, y : arrays
            Массивы данных.

        Returns
        -------
        r, p : float
            Коэффициент корреляции и p-value.
        """
        r, p = stats.pearsonr(x, y)
        return r, p

    @staticmethod
    def linear_regression(x: np.ndarray, y: np.ndarray) -> dict:
        """
        Линейная регрессия.

        Parameters
        ----------
        x, y : arrays
            Массивы данных.

        Returns
        -------
        dict
            Параметры регрессии (slope, intercept, r_value, p_value, std_err).
        """
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        return {
            "slope": slope,
            "intercept": intercept,
            "r_value": r_value,
            "p_value": p_value,
            "std_err": std_err,
        }
