"""
Анализ характеристик событий.
"""

from typing import List, Dict
from heliopy.events.flare_detector import Flare
from heliopy.events.cme_detector import CME
from heliopy.utils.stats_utils import StatsUtils


class EventAnalyzer:
    """Класс для анализа характеристик событий."""
    
    def __init__(self):
        """Инициализация анализатора."""
        pass
    
    def analyze_flare_statistics(self, flares: List[Flare]) -> Dict:
        """
        Статистический анализ вспышек.
        
        Parameters
        ----------
        flares : list
            Список вспышек.
        
        Returns
        -------
        dict
            Словарь со статистикой.
        """
        if len(flares) == 0:
            return {}
        
        # Классификация по классам
        class_counts = {}
        for flare in flares:
            class_counts[flare.class_] = class_counts.get(flare.class_, 0) + 1
        
        # Статистика по потоку
        peak_fluxes = [f.peak_flux for f in flares]
        durations = [f.duration.total_seconds() / 3600 for f in flares]  # в часах
        
        return {
            'total_count': len(flares),
            'class_distribution': class_counts,
            'peak_flux_mean': sum(peak_fluxes) / len(peak_fluxes),
            'peak_flux_max': max(peak_fluxes),
            'duration_mean': sum(durations) / len(durations),
            'duration_max': max(durations),
        }
    
    def analyze_cme_statistics(self, cmes: List[CME]) -> Dict:
        """
        Статистический анализ CME.
        
        Parameters
        ----------
        cmes : list
            Список CME.
        
        Returns
        -------
        dict
            Словарь со статистикой.
        """
        if len(cmes) == 0:
            return {}
        
        speeds = [c.speed for c in cmes]
        accelerations = [c.acceleration for c in cmes]
        angular_widths = [c.angular_width for c in cmes]
        
        return {
            'total_count': len(cmes),
            'speed_mean': sum(speeds) / len(speeds),
            'speed_max': max(speeds),
            'acceleration_mean': sum(accelerations) / len(accelerations),
            'angular_width_mean': sum(angular_widths) / len(angular_widths),
        }
    
    def correlate_flares_cmes(self, flares: List[Flare], cmes: List[CME],
                              time_window_hours: float = 24.0) -> List[Dict]:
        """
        Поиск корреляций между вспышками и CME.
        
        Parameters
        ----------
        flares : list
            Список вспышек.
        cmes : list
            Список CME.
        time_window_hours : float
            Временное окно для поиска корреляций в часах.
        
        Returns
        -------
        list
            Список словарей с найденными корреляциями.
        """
        correlations = []
        
        for flare in flares:
            for cme in cmes:
                time_diff = (cme.start_time - flare.peak_time).to(u.hour).value
                
                if 0 <= time_diff <= time_window_hours:
                    correlations.append({
                        'flare': flare,
                        'cme': cme,
                        'time_difference_hours': time_diff,
                    })
        
        return correlations

