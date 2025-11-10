"""
Обнаружение солнечных вспышек.
"""

import numpy as np
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
from astropy.time import Time
from dataclasses import dataclass


@dataclass
class Flare:
    """Класс для представления солнечной вспышки."""
    start_time: Time
    peak_time: Time
    end_time: Time
    class_: str  # A, B, C, M, X
    peak_flux: float
    duration: timedelta
    location: Optional[Dict] = None  # {'lon': float, 'lat': float}
    active_region: Optional[str] = None


@dataclass
class GOESData:
    """Класс для данных GOES."""
    time: Time
    xrsa: np.ndarray  # XRS-A канал
    xrsb: np.ndarray  # XRS-B канал
    satellite: str = 'goes16'


class FlareDetector:
    """Класс для обнаружения солнечных вспышек."""
    
    # Пороги для классификации вспышек (W/m²)
    FLARE_THRESHOLDS = {
        'A': 1e-8,
        'B': 1e-7,
        'C': 1e-6,
        'M': 1e-5,
        'X': 1e-4,
    }
    
    def __init__(self, threshold_factor: float = 1.5):
        """
        Инициализация детектора вспышек.
        
        Parameters
        ----------
        threshold_factor : float
            Фактор для определения порога вспышки.
        """
        self.threshold_factor = threshold_factor
    
    def detect_flares(self, goes_data: GOESData) -> List[Flare]:
        """
        Обнаружение вспышек в данных GOES.
        
        Parameters
        ----------
        goes_data : GOESData
            Данные GOES.
        
        Returns
        -------
        list
            Список обнаруженных вспышек.
        """
        flares = []
        
        # Используем XRS-B канал (короткие волны) для обнаружения
        flux = goes_data.xrsb
        
        if len(flux) == 0:
            return flares
        
        # Базовый уровень (медиана)
        baseline = np.median(flux)
        threshold = baseline * self.threshold_factor
        
        # Поиск пиков выше порога
        above_threshold = flux > threshold
        
        if not np.any(above_threshold):
            return flares
        
        # Поиск непрерывных интервалов
        in_flare = False
        flare_start_idx = None
        
        for i, is_above in enumerate(above_threshold):
            if is_above and not in_flare:
                # Начало вспышки
                in_flare = True
                flare_start_idx = i
            elif not is_above and in_flare:
                # Конец вспышки
                in_flare = False
                # Определение пика
                flare_flux = flux[flare_start_idx:i]
                peak_idx = flare_start_idx + np.argmax(flare_flux)
                
                # Создание объекта вспышки
                flare = self._create_flare(
                    goes_data,
                    flare_start_idx,
                    peak_idx,
                    i
                )
                
                if flare:
                    flares.append(flare)
        
        # Обработка случая, когда вспышка продолжается до конца данных
        if in_flare:
            flare_flux = flux[flare_start_idx:]
            peak_idx = flare_start_idx + np.argmax(flare_flux)
            flare = self._create_flare(
                goes_data,
                flare_start_idx,
                peak_idx,
                len(flux) - 1
            )
            if flare:
                flares.append(flare)
        
        return flares
    
    def _create_flare(self, goes_data: GOESData, start_idx: int, 
                     peak_idx: int, end_idx: int) -> Optional[Flare]:
        """
        Создание объекта вспышки из индексов.
        
        Parameters
        ----------
        goes_data : GOESData
            Данные GOES.
        start_idx : int
            Индекс начала.
        peak_idx : int
            Индекс пика.
        end_idx : int
            Индекс конца.
        
        Returns
        -------
        Flare или None
            Объект вспышки или None, если не соответствует критериям.
        """
        if len(goes_data.xrsb) == 0:
            return None
        
        peak_flux = goes_data.xrsb[peak_idx]
        
        # Определение класса вспышки
        flare_class = self._classify_flare(peak_flux)
        
        if flare_class is None:
            return None
        
        # Времена (упрощенная реализация)
        # В полной версии нужно использовать реальные временные метки
        start_time = goes_data.time
        peak_time = goes_data.time
        end_time = goes_data.time
        
        duration = timedelta(seconds=(end_idx - start_idx) * 60)  # Предполагаем 1 минута на точку
        
        return Flare(
            start_time=start_time,
            peak_time=peak_time,
            end_time=end_time,
            class_=flare_class,
            peak_flux=peak_flux,
            duration=duration
        )
    
    def _classify_flare(self, peak_flux: float) -> Optional[str]:
        """
        Классификация вспышки по пиковому потоку.
        
        Parameters
        ----------
        peak_flux : float
            Пиковый поток в W/m².
        
        Returns
        -------
        str или None
            Класс вспышки (A, B, C, M, X) или None.
        """
        if peak_flux >= self.FLARE_THRESHOLDS['X']:
            return 'X'
        elif peak_flux >= self.FLARE_THRESHOLDS['M']:
            return 'M'
        elif peak_flux >= self.FLARE_THRESHOLDS['C']:
            return 'C'
        elif peak_flux >= self.FLARE_THRESHOLDS['B']:
            return 'B'
        elif peak_flux >= self.FLARE_THRESHOLDS['A']:
            return 'A'
        else:
            return None

