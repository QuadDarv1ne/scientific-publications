"""
Модульные тесты для core модулей.
"""

import pytest
import numpy as np
from heliopy.core.data_processor import DataProcessor
from heliopy.core.coordinate_systems import CoordinateSystem
from heliopy.core.units import SolarUnits
from heliopy.utils.time_utils import TimeUtils
from astropy.time import Time


class TestDataProcessor:
    """Тесты для DataProcessor."""
    
    def test_normalize_minmax(self):
        """Тест нормализации методом minmax."""
        processor = DataProcessor()
        data = np.array([1, 2, 3, 4, 5])
        normalized = processor.normalize(data, method='minmax')
        
        assert np.allclose(normalized, [0, 0.25, 0.5, 0.75, 1.0])
    
    def test_normalize_zscore(self):
        """Тест нормализации методом zscore."""
        processor = DataProcessor()
        data = np.array([1, 2, 3, 4, 5])
        normalized = processor.normalize(data, method='zscore')
        
        assert np.isclose(np.mean(normalized), 0.0, atol=1e-10)
        assert np.isclose(np.std(normalized), 1.0, atol=1e-10)


class TestCoordinateSystem:
    """Тесты для CoordinateSystem."""
    
    def test_heliographic_to_cartesian(self):
        """Тест преобразования гелиографических координат."""
        lon = np.array([0, np.pi/2])
        lat = np.array([0, np.pi/4])
        radius = 1.0
        
        x, y, z = CoordinateSystem.heliographic_to_cartesian(lon, lat, radius)
        
        assert len(x) == 2
        assert len(y) == 2
        assert len(z) == 2


class TestTimeUtils:
    """Тесты для TimeUtils."""
    
    def test_parse_time_string(self):
        """Тест парсинга времени из строки."""
        time = TimeUtils.parse_time("2023-10-15")
        assert isinstance(time, Time)
    
    def test_carrington_rotation(self):
        """Тест вычисления вращения Кэррингтона."""
        time = Time("2023-10-15")
        rotation = TimeUtils.carrington_rotation(time)
        
        assert rotation > 2000  # Должно быть большое число

