"""
Оценка воздействия космической погоды на Землю.
"""

from typing import Dict, List
from heliopy.events.flare_detector import Flare
from heliopy.events.cme_detector import CME
from heliopy.space_weather.forecast_models import ForecastResult


class ImpactAssessment:
    """Класс для оценки воздействия космической погоды."""
    
    def __init__(self):
        """Инициализация оценки воздействия."""
        pass
    
    def assess_satellite_risk(self, forecast: ForecastResult) -> Dict:
        """
        Оценка рисков для спутников.
        
        Parameters
        ----------
        forecast : ForecastResult
            Результат прогноза.
        
        Returns
        -------
        dict
            Словарь с оценкой рисков.
        """
        risk_levels = {
            'low': 'low',
            'moderate': 'medium',
            'high': 'high',
            'severe': 'critical',
        }
        
        risk_level = risk_levels.get(forecast.impact_level, 'low')
        
        risks = {
            'risk_level': risk_level,
            'single_event_upset_probability': self._estimate_seu_probability(forecast),
            'solar_panel_degradation': self._estimate_panel_degradation(forecast),
            'atmospheric_drag_increase': self._estimate_drag_increase(forecast),
        }
        
        return risks
    
    def assess_power_grid_risk(self, forecast: ForecastResult) -> Dict:
        """
        Оценка рисков для энергосистем.
        
        Parameters
        ----------
        forecast : ForecastResult
            Результат прогноза.
        
        Returns
        -------
        dict
            Словарь с оценкой рисков.
        """
        # Критический Dst может вызвать геомагнитные бури
        # которые влияют на энергосистемы
        risk_level = 'low'
        
        if forecast.dst_index_forecast < -100:
            risk_level = 'high'
        elif forecast.dst_index_forecast < -50:
            risk_level = 'moderate'
        
        return {
            'risk_level': risk_level,
            'geomagnetically_induced_currents': self._estimate_gic(forecast),
            'transformer_risk': self._estimate_transformer_risk(forecast),
        }
    
    def assess_communication_risk(self, forecast: ForecastResult) -> Dict:
        """
        Оценка рисков для систем связи.
        
        Parameters
        ----------
        forecast : ForecastResult
            Результат прогноза.
        
        Returns
        -------
        dict
            Словарь с оценкой рисков.
        """
        return {
            'risk_level': forecast.impact_level,
            'ionospheric_scintillation': self._estimate_scintillation(forecast),
            'radio_blackout_probability': self._estimate_radio_blackout(forecast),
        }
    
    def _estimate_seu_probability(self, forecast: ForecastResult) -> float:
        """Оценка вероятности единичных сбоев в электронике."""
        # Упрощенная модель
        if forecast.impact_level == 'severe':
            return 0.3
        elif forecast.impact_level == 'high':
            return 0.15
        elif forecast.impact_level == 'moderate':
            return 0.05
        else:
            return 0.01
    
    def _estimate_panel_degradation(self, forecast: ForecastResult) -> float:
        """Оценка деградации солнечных панелей (процент)."""
        return 0.1 * {'low': 1, 'moderate': 2, 'high': 5, 'severe': 10}.get(forecast.impact_level, 1)
    
    def _estimate_drag_increase(self, forecast: ForecastResult) -> float:
        """Оценка увеличения атмосферного сопротивления (процент)."""
        return 5.0 * {'low': 1, 'moderate': 2, 'high': 5, 'severe': 10}.get(forecast.impact_level, 1)
    
    def _estimate_gic(self, forecast: ForecastResult) -> float:
        """Оценка геомагнитно-индуцированных токов (А)."""
        return abs(forecast.dst_index_forecast) * 0.5
    
    def _estimate_transformer_risk(self, forecast: ForecastResult) -> str:
        """Оценка риска для трансформаторов."""
        if forecast.dst_index_forecast < -200:
            return 'high'
        elif forecast.dst_index_forecast < -100:
            return 'moderate'
        else:
            return 'low'
    
    def _estimate_scintillation(self, forecast: ForecastResult) -> float:
        """Оценка ионосферной сцинтилляции."""
        return {'low': 0.1, 'moderate': 0.3, 'high': 0.6, 'severe': 0.9}.get(forecast.impact_level, 0.1)
    
    def _estimate_radio_blackout(self, forecast: ForecastResult) -> float:
        """Оценка вероятности радиопомех."""
        return {'low': 0.05, 'moderate': 0.2, 'high': 0.5, 'severe': 0.8}.get(forecast.impact_level, 0.05)

