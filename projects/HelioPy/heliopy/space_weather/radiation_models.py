"""
Модели радиационных поясов и протонных событий.
"""

from typing import Dict

import numpy as np

from heliopy.events.flare_detector import Flare


class RadiationModel:
    """Класс для моделирования радиационных эффектов."""

    def __init__(self):
        """Инициализация модели."""
        pass

    def forecast_proton_event(self, flare: Flare) -> Dict:
        """
        Прогноз солнечного протонного события.

        Parameters
        ----------
        flare : Flare
            Солнечная вспышка.

        Returns
        -------
        dict
            Словарь с прогнозом протонного события.
        """
        # Вероятность протонного события зависит от класса вспышки
        probabilities = {
            "A": 0.01,
            "B": 0.05,
            "C": 0.15,
            "M": 0.4,
            "X": 0.7,
        }

        probability = probabilities.get(flare.class_, 0.01)

        # Ожидаемый пиковый поток протонов (pfu)
        peak_flux = {
            "A": 1,
            "B": 10,
            "C": 100,
            "M": 1000,
            "X": 10000,
        }.get(flare.class_, 1)

        return {
            "probability": probability,
            "expected_peak_flux_pfu": peak_flux,
            "start_time": flare.peak_time,
            "duration_hours": 24.0,
        }

    def calculate_radiation_dose(
        self, proton_flux: np.ndarray, time: np.ndarray, shielding_thickness: float = 0.0
    ) -> Dict:
        """
        Расчет дозы облучения для космического аппарата.

        Parameters
        ----------
        proton_flux : array
            Поток протонов (pfu).
        time : array
            Временные метки.
        shielding_thickness : float
            Толщина экранирования (г/см²).

        Returns
        -------
        dict
            Словарь с расчетами дозы.
        """
        # Упрощенная модель
        # В полной версии используется более сложная физическая модель

        # Интегральная доза
        if len(proton_flux) == 0:
            return {"total_dose": 0.0, "dose_rate_max": 0.0}

        # Коэффициент ослабления экранирования
        attenuation = np.exp(-shielding_thickness / 10.0)  # Упрощение

        # Доза (упрощенная модель)
        dose_rate = proton_flux * 0.1 * attenuation  # мЗв/ч
        total_dose = np.trapz(dose_rate, time) if len(time) > 1 else dose_rate[0] * 24

        return {
            "total_dose_mSv": total_dose,
            "dose_rate_max_mSv_per_hour": np.max(dose_rate),
            "shielding_thickness_g_per_cm2": shielding_thickness,
        }
