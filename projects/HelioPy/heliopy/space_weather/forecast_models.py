"""
Модели прогнозирования космической погоды.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from astropy.time import Time, TimeDelta

from heliopy.events.cme_detector import CME
from heliopy.events.flare_detector import Flare


@dataclass
class ACEData:
    """Класс для данных ACE."""

    time: Time
    proton_density: np.ndarray  # см⁻³
    proton_speed: np.ndarray  # км/с
    proton_temperature: np.ndarray  # К
    magnetic_field: np.ndarray  # нТл


@dataclass
class ForecastResult:
    """Результат прогноза."""

    arrival_time: Time
    impact_level: str  # 'low', 'moderate', 'high', 'severe'
    kp_index_forecast: float
    dst_index_forecast: float
    confidence: float  # 0-1
    summary: str


class ForecastModel:
    """Класс для прогнозирования космической погоды."""

    def __init__(self):
        """Инициализация модели прогноза."""
        pass

    def forecast_geoeffectiveness(self, flare: Flare, cme: Optional[CME] = None) -> ForecastResult:
        """
        Прогноз геоэффективности события.

        Parameters
        ----------
        flare : Flare
            Солнечная вспышка.
        cme : CME, optional
            Связанный CME.

        Returns
        -------
        ForecastResult
            Результат прогноза.
        """
        # Упрощенная модель прогноза
        # В полной версии используется более сложная физическая модель

        # Базовый прогноз на основе класса вспышки
        impact_levels = {
            "A": "low",
            "B": "low",
            "C": "moderate",
            "M": "high",
            "X": "severe",
        }

        impact_level = impact_levels.get(flare.class_, "low")

        # Прогноз индексов
        kp_forecast = self._estimate_kp(flare, cme)
        dst_forecast = self._estimate_dst(flare, cme)

        # Время прибытия (если есть CME)
        if cme:
            # Упрощенный расчет времени прибытия
            # Расстояние от Солнца до Земли ~ 1 AU
            distance_au = 1.0
            distance_km = distance_au * 1.496e8  # км

            # Время прибытия
            arrival_time_seconds = distance_km / cme.speed
            arrival_time = flare.peak_time + TimeDelta(seconds=arrival_time_seconds)
        else:
            arrival_time = flare.peak_time + TimeDelta(hours=24)

        # Уверенность прогноза
        confidence = 0.7 if cme else 0.5

        summary = f"Прогноз воздействия: {impact_level}. "
        summary += f"Ожидаемый Kp: {kp_forecast:.1f}, Dst: {dst_forecast:.0f} нТл. "
        if cme:
            summary += f"Время прибытия CME: {arrival_time.iso}"

        return ForecastResult(
            arrival_time=arrival_time,
            impact_level=impact_level,
            kp_index_forecast=kp_forecast,
            dst_index_forecast=dst_forecast,
            confidence=confidence,
            summary=summary,
        )

    def _estimate_kp(self, flare: Flare, cme: Optional[CME] = None) -> float:
        """Оценка индекса Kp."""
        # Упрощенная модель
        kp_base = {
            "A": 2.0,
            "B": 3.0,
            "C": 4.0,
            "M": 5.0,
            "X": 7.0,
        }.get(flare.class_, 2.0)

        if cme:
            # Увеличение Kp для быстрых CME
            if cme.speed > 1000:
                kp_base += 1.0
            elif cme.speed > 500:
                kp_base += 0.5

        return min(kp_base, 9.0)

    def _estimate_dst(self, flare: Flare, cme: Optional[CME] = None) -> float:
        """Оценка индекса Dst."""
        # Упрощенная модель
        dst_base = {
            "A": -20,
            "B": -30,
            "C": -50,
            "M": -100,
            "X": -200,
        }.get(flare.class_, -20)

        if cme:
            # Более сильное воздействие для быстрых CME
            if cme.speed > 1000:
                dst_base *= 2
            elif cme.speed > 500:
                dst_base *= 1.5

        return dst_base


def forecast_geoeffectiveness(flare: Flare, cme: Optional[CME] = None) -> ForecastResult:
    """
    Удобная функция для прогноза геоэффективности.

    Parameters
    ----------
    flare : Flare
        Солнечная вспышка.
    cme : CME, optional
        Связанный CME.

    Returns
    -------
    ForecastResult
        Результат прогноза.
    """
    model = ForecastModel()
    return model.forecast_geoeffectiveness(flare, cme)
