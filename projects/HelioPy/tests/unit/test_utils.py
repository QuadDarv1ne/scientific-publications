"""
Модульные тесты для utils модулей.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from astropy.time import Time
from heliopy.utils.math_utils import MathUtils
from heliopy.utils.stats_utils import StatsUtils
from heliopy.utils.time_utils import TimeUtils


class TestMathUtils:
    """Тесты для MathUtils."""

    def test_spherical_to_cartesian(self):
        """Тест преобразования сферических координат в декартовы."""
        r = 1.0
        theta = np.pi / 2  # 90 градусов
        phi = 0.0

        x, y, z = MathUtils.spherical_to_cartesian(r, theta, phi)

        # На экваторе (theta=90°, phi=0°) должно быть x=1, y=0, z≈0
        assert np.isclose(x, 1.0, atol=1e-10)
        assert np.isclose(y, 0.0, atol=1e-10)
        assert np.isclose(z, 0.0, atol=1e-10)

    def test_cartesian_to_spherical(self):
        """Тест преобразования декартовых координат в сферические."""
        x, y, z = 1.0, 0.0, 0.0

        r, theta, phi = MathUtils.cartesian_to_spherical(x, y, z)

        assert np.isclose(r, 1.0)
        assert np.isclose(theta, np.pi / 2)  # 90 градусов от оси z
        assert np.isclose(phi, 0.0, atol=1e-10)

    def test_angular_separation(self):
        """Тест вычисления углового расстояния."""
        # Расстояние между одной и той же точкой должно быть 0
        lon1, lat1 = 0.0, 0.0
        lon2, lat2 = 0.0, 0.0

        distance = MathUtils.angular_separation(lon1, lat1, lon2, lat2)
        assert np.isclose(distance, 0.0, atol=1e-10)

        # Расстояние между противоположными точками на экваторе
        lon1, lat1 = 0.0, 0.0
        lon2, lat2 = np.pi, 0.0

        distance = MathUtils.angular_separation(lon1, lat1, lon2, lat2)
        assert np.isclose(distance, np.pi, atol=1e-5)

    def test_great_circle_distance(self):
        """Тест вычисления расстояния по большому кругу."""
        lon1, lat1 = 0.0, 0.0
        lon2, lat2 = np.pi, 0.0
        radius = 1.0

        distance = MathUtils.great_circle_distance(lon1, lat1, lon2, lat2, radius)

        # Расстояние должно быть π * radius
        assert np.isclose(distance, np.pi * radius, atol=1e-5)


class TestStatsUtils:
    """Тесты для StatsUtils."""

    def test_robust_statistics(self):
        """Тест вычисления устойчивых статистик."""
        data = np.array([1, 2, 3, 4, 5, 100])  # 100 - выброс

        stats = StatsUtils.robust_statistics(data)

        assert "median" in stats
        assert "mad" in stats
        assert "q25" in stats
        assert "q75" in stats

        # Медиана не должна сильно зависеть от выброса
        assert stats["median"] == 3.5  # Медиана между 3 и 4

    def test_remove_outliers(self):
        """Тест удаления выбросов."""
        data = np.array([1, 2, 3, 4, 5, 100])

        cleaned = StatsUtils.remove_outliers(data, method="iqr", factor=1.5)

        # Выброс 100 должен быть удален
        assert 100 not in cleaned
        assert len(cleaned) < len(data)

    def test_correlation_coefficient(self):
        """Тест коэффициента корреляции Пирсона."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])  # Идеальная линейная зависимость

        corr, p_value = StatsUtils.correlation_coefficient(x, y)

        # Корреляция должна быть близка к 1
        assert np.isclose(corr, 1.0, atol=1e-10)

    def test_linear_regression(self):
        """Тест линейной регрессии."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])  # y = 2*x

        result = StatsUtils.linear_regression(x, y)

        assert "slope" in result
        assert "intercept" in result
        assert np.isclose(result["slope"], 2.0, atol=1e-10)
        assert np.isclose(result["intercept"], 0.0, atol=1e-10)


class TestTimeUtils:
    """Тесты для TimeUtils."""

    def test_parse_time_datetime(self):
        """Тест парсинга datetime."""
        dt = datetime(2023, 10, 15, 12, 0, 0)
        time = TimeUtils.parse_time(dt)

        assert isinstance(time, Time)

    def test_time_range(self):
        """Тест генерации временного массива."""
        start = "2023-10-15 00:00:00"
        end = "2023-10-15 01:00:00"
        step = timedelta(minutes=30)

        times = TimeUtils.time_range(start, end, step)

        # Должно быть >= 2 элемента
        assert len(times) >= 2

    def test_to_datetime(self):
        """Тест конвертации Time в datetime."""
        time = Time("2023-10-15 12:00:00")
        dt = TimeUtils.to_datetime(time)

        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 10
        assert dt.day == 15

    def test_to_julian_date(self):
        """Тест конвертации в юлианскую дату."""
        time = "2023-10-15 12:00:00"
        jd = TimeUtils.to_julian_date(time)

        assert isinstance(jd, float)
        assert jd > 2400000  # Юлианская дата должна быть большим числом
