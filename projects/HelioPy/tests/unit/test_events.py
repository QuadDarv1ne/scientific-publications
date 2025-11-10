"""
Модульные тесты для events модулей.
"""

import pytest
import numpy as np
from astropy.time import Time
from heliopy.events.flare_detector import FlareDetector, GOESData, Flare
from heliopy.events.cme_detector import CMEDetector, CME


class TestFlareDetector:
    """Тесты для FlareDetector."""
    
    def test_classify_flare(self):
        """Тест классификации вспышек."""
        detector = FlareDetector()
        
        assert detector._classify_flare(1e-3) == 'X'
        assert detector._classify_flare(1e-5) == 'M'
        assert detector._classify_flare(1e-6) == 'C'
        assert detector._classify_flare(1e-7) == 'B'
        assert detector._classify_flare(1e-8) == 'A'
        assert detector._classify_flare(1e-9) is None
    
    def test_detect_flares_empty(self):
        """Тест обнаружения вспышек в пустых данных."""
        detector = FlareDetector()
        goes_data = GOESData(
            time=Time("2023-10-15"),
            xrsa=np.array([]),
            xrsb=np.array([])
        )
        
        flares = detector.detect_flares(goes_data)
        assert len(flares) == 0

