"""
Unit tests for ISS Orbital Analysis Module
Тесты для модуля орбитального анализа МКС
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils import (
    CoordinateConverter, OrbitalCalculations, 
    DataValidator, TimeUtils, StatisticsCalculator
)


class TestCoordinateConverter(unittest.TestCase):
    """Тесты для конвертера координат"""
    
    def test_geodetic_to_cartesian(self):
        """Тест конвертации геодезических координат в декартовы"""
        # Москва на уровне моря
        lat, lon = 55.7558, 37.6173
        x, y, z = CoordinateConverter.geodetic_to_cartesian(lat, lon, 0)
        
        # Проверка что координаты не нулевые
        self.assertNotEqual(x, 0)
        self.assertNotEqual(y, 0)
        self.assertNotEqual(z, 0)
        
        # Проверка радиуса (должен быть примерно равен радиусу Земли)
        r = np.sqrt(x**2 + y**2 + z**2)
        self.assertAlmostEqual(r, 6371.0, delta=1.0)
    
    def test_cartesian_to_geodetic(self):
        """Тест конвертации декартовых координат в геодезические"""
        # Конвертация туда и обратно
        lat1, lon1 = 55.7558, 37.6173
        x, y, z = CoordinateConverter.geodetic_to_cartesian(lat1, lon1, 0)
        lat2, lon2, alt = CoordinateConverter.cartesian_to_geodetic(x, y, z)
        
        # Проверка что получили исходные координаты
        self.assertAlmostEqual(lat1, lat2, delta=0.01)
        self.assertAlmostEqual(lon1, lon2, delta=0.01)
        self.assertAlmostEqual(alt, 0, delta=0.1)
    
    def test_haversine_distance(self):
        """Тест расчета расстояния между точками"""
        # Москва - Санкт-Петербург
        lat1, lon1 = 55.7558, 37.6173
        lat2, lon2 = 59.9343, 30.3351
        
        distance = CoordinateConverter.haversine_distance(lat1, lon1, lat2, lon2)
        
        # Примерное расстояние ~630 км
        self.assertGreater(distance, 600)
        self.assertLess(distance, 700)
    
    def test_haversine_same_point(self):
        """Тест расстояния между одинаковыми точками"""
        lat, lon = 55.7558, 37.6173
        distance = CoordinateConverter.haversine_distance(lat, lon, lat, lon)
        
        # Расстояние должно быть близко к нулю
        self.assertAlmostEqual(distance, 0, delta=0.01)


class TestOrbitalCalculations(unittest.TestCase):
    """Тесты для орбитальных вычислений"""
    
    def test_orbital_velocity(self):
        """Тест расчета орбитальной скорости"""
        altitude = 408  # МКС
        velocity = OrbitalCalculations.calculate_orbital_velocity(altitude)
        
        # Первая космическая скорость ~7.66 км/с для МКС
        self.assertGreater(velocity, 7.5)
        self.assertLess(velocity, 8.0)
    
    def test_orbital_period(self):
        """Тест расчета периода обращения"""
        altitude = 408
        period = OrbitalCalculations.calculate_orbital_period(altitude)
        
        # Период обращения МКС ~93 минуты
        self.assertGreater(period, 90)
        self.assertLess(period, 95)
    
    def test_escape_velocity(self):
        """Тест расчета второй космической скорости"""
        altitude = 408
        escape_vel = OrbitalCalculations.calculate_escape_velocity(altitude)
        
        # Вторая космическая ~10.8 км/с
        self.assertGreater(escape_vel, 10.5)
        self.assertLess(escape_vel, 11.2)
    
    def test_atmospheric_drag(self):
        """Тест коэффициента атмосферного торможения"""
        # Чем выше орбита, тем меньше торможение
        drag_low = OrbitalCalculations.atmospheric_drag_coefficient(200)
        drag_high = OrbitalCalculations.atmospheric_drag_coefficient(500)
        
        self.assertGreater(drag_low, drag_high)


class TestDataValidator(unittest.TestCase):
    """Тесты для валидатора данных"""
    
    def test_valid_coordinates(self):
        """Тест валидных координат"""
        self.assertTrue(DataValidator.validate_coordinates(55.7558, 37.6173))
        self.assertTrue(DataValidator.validate_coordinates(0, 0))
        self.assertTrue(DataValidator.validate_coordinates(-90, -180))
        self.assertTrue(DataValidator.validate_coordinates(90, 180))
    
    def test_invalid_latitude(self):
        """Тест невалидной широты"""
        self.assertFalse(DataValidator.validate_coordinates(91, 0))
        self.assertFalse(DataValidator.validate_coordinates(-91, 0))
        self.assertFalse(DataValidator.validate_coordinates(200, 0))
    
    def test_invalid_longitude(self):
        """Тест невалидной долготы"""
        self.assertFalse(DataValidator.validate_coordinates(0, 181))
        self.assertFalse(DataValidator.validate_coordinates(0, -181))
        self.assertFalse(DataValidator.validate_coordinates(0, 360))
    
    def test_valid_altitude(self):
        """Тест валидной высоты"""
        self.assertTrue(DataValidator.validate_altitude(408))
        self.assertTrue(DataValidator.validate_altitude(400))
        self.assertTrue(DataValidator.validate_altitude(420))
    
    def test_invalid_altitude(self):
        """Тест невалидной высоты"""
        self.assertFalse(DataValidator.validate_altitude(-10))
        self.assertFalse(DataValidator.validate_altitude(2000))
    
    def test_valid_velocity(self):
        """Тест валидной скорости"""
        self.assertTrue(DataValidator.validate_velocity(7.66))
        self.assertTrue(DataValidator.validate_velocity(8.0))
    
    def test_invalid_velocity(self):
        """Тест невалидной скорости"""
        self.assertFalse(DataValidator.validate_velocity(-1))
        self.assertFalse(DataValidator.validate_velocity(25))


class TestTimeUtils(unittest.TestCase):
    """Тесты для утилит работы со временем"""
    
    def test_timestamp_conversion(self):
        """Тест конвертации timestamp"""
        dt = datetime.now()
        timestamp = TimeUtils.datetime_to_timestamp(dt)
        dt2 = TimeUtils.timestamp_to_datetime(timestamp)
        
        # Проверка что время не сильно изменилось (с точностью до секунды)
        self.assertAlmostEqual(
            dt.timestamp(), 
            dt2.timestamp(), 
            delta=1.0
        )
    
    def test_format_duration_hours(self):
        """Тест форматирования длительности (часы)"""
        duration = TimeUtils.format_duration(3665)  # 1ч 1м 5с
        self.assertIn('1ч', duration)
        self.assertIn('1м', duration)
        self.assertIn('5с', duration)
    
    def test_format_duration_minutes(self):
        """Тест форматирования длительности (минуты)"""
        duration = TimeUtils.format_duration(125)  # 2м 5с
        self.assertIn('2м', duration)
        self.assertIn('5с', duration)
        self.assertNotIn('ч', duration)
    
    def test_format_duration_seconds(self):
        """Тест форматирования длительности (секунды)"""
        duration = TimeUtils.format_duration(45)  # 45с
        self.assertIn('45с', duration)
        self.assertNotIn('м', duration)
        self.assertNotIn('ч', duration)
    
    def test_timestamp_filename(self):
        """Тест генерации имени файла с timestamp"""
        filename = TimeUtils.get_timestamp_filename('test', 'txt')
        
        self.assertTrue(filename.startswith('test_'))
        self.assertTrue(filename.endswith('.txt'))
        self.assertIn('_', filename)


class TestStatisticsCalculator(unittest.TestCase):
    """Тесты для калькулятора статистики"""
    
    def test_basic_statistics(self):
        """Тест базовой статистики"""
        data = [1, 2, 3, 4, 5]
        stats = StatisticsCalculator.calculate_statistics(data)
        
        # Проверка что статистика не None
        self.assertIsNotNone(stats)
        
        # Проверка значений статистики
        if stats is not None:
            self.assertEqual(stats['mean'], 3.0)
            self.assertEqual(stats['median'], 3.0)
            self.assertEqual(stats['min'], 1)
            self.assertEqual(stats['max'], 5)
            self.assertEqual(stats['range'], 4)
            self.assertEqual(stats['count'], 5)
    
    def test_empty_data(self):
        """Тест пустых данных"""
        stats = StatisticsCalculator.calculate_statistics([])
        self.assertIsNone(stats)
    
    def test_moving_average(self):
        """Тест скользящего среднего"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        smoothed = StatisticsCalculator.moving_average(data, window_size=3)
        
        # Проверка что результат короче исходных данных
        self.assertLess(len(smoothed), len(data))
        
        # Проверка что значения сглажены
        self.assertAlmostEqual(smoothed[0], 2.0, delta=0.1)
    
    def test_moving_average_small_data(self):
        """Тест скользящего среднего на малых данных"""
        data = [1, 2]
        smoothed = StatisticsCalculator.moving_average(data, window_size=5)
        
        # Если данных меньше окна, возвращаем исходные
        np.testing.assert_array_equal(smoothed, data)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_full_coordinate_cycle(self):
        """Тест полного цикла работы с координатами"""
        # Исходные координаты
        lat1, lon1 = 55.7558, 37.6173
        alt1 = 408
        
        # Валидация
        self.assertTrue(DataValidator.validate_coordinates(lat1, lon1))
        self.assertTrue(DataValidator.validate_altitude(alt1))
        
        # Конвертация в декартовы
        x, y, z = CoordinateConverter.geodetic_to_cartesian(lat1, lon1, alt1)
        
        # Конвертация обратно
        lat2, lon2, alt2 = CoordinateConverter.cartesian_to_geodetic(x, y, z)
        
        # Проверка точности
        self.assertAlmostEqual(lat1, lat2, delta=0.1)
        self.assertAlmostEqual(lon1, lon2, delta=0.1)
        self.assertAlmostEqual(alt1, alt2, delta=1.0)
    
    def test_orbital_calculations_consistency(self):
        """Тест согласованности орбитальных вычислений"""
        altitude = 408
        
        # Расчет параметров
        velocity = OrbitalCalculations.calculate_orbital_velocity(altitude)
        period = OrbitalCalculations.calculate_orbital_period(altitude)
        
        # Проверка что параметры согласованы
        # Расстояние = скорость × время
        orbit_circumference = 2 * np.pi * (6371 + altitude)
        calculated_period = orbit_circumference / velocity / 60  # в минутах
        
        self.assertAlmostEqual(period, calculated_period, delta=0.1)


class TestNewFunctions(unittest.TestCase):
    """Тесты для новых функций"""
    
    def test_parse_tle_data(self):
        """Тест парсинга TLE данных"""
        # Пример TLE данных МКС
        line1 = "1 25544U 98067A   24310.54321876  .00012345  00000-0  12345-3 0  9999"
        line2 = "2 25544  51.6400 123.4567 0001234  12.3456 123.4567 15.54567890123456"
        
        # Создаем трекер и тестируем парсинг
        from src.iss_orbital_analysis import ISSTracker
        tracker = ISSTracker()
        params = tracker._parse_tle_data(line1, line2)
        
        # Проверяем, что параметры были извлечены
        self.assertIn('inclination', params)
        self.assertIn('eccentricity', params)
        self.assertIn('mean_motion', params)
        self.assertIn('orbital_period_min', params)
        self.assertIn('altitude_km', params)
        
        # Проверяем разумность значений
        self.assertGreater(params['inclination'], 0)
        self.assertLess(params['inclination'], 90)
        self.assertGreater(params['eccentricity'], 0)
        self.assertLess(params['eccentricity'], 1)
        self.assertGreater(params['mean_motion'], 10)
        self.assertLess(params['mean_motion'], 20)
        self.assertGreater(params['orbital_period_min'], 80)
        self.assertLess(params['orbital_period_min'], 100)
        self.assertGreater(params['altitude_km'], 300)
        self.assertLess(params['altitude_km'], 500)
    
    def test_analyze_altitude_trend(self):
        """Тест анализа тренда высоты орбиты"""
        from src.iss_orbital_analysis import ISSTracker
        tracker = ISSTracker()
        
        # Тестируем функцию анализа тренда
        result = tracker.analyze_altitude_trend(save=False, show=False)
        
        # Проверяем, что результат не None
        self.assertIsNotNone(result)
        
        # Проверяем наличие ключевых полей в результате
        if result is not None:
            self.assertIn('initial_altitude', result)
            self.assertIn('final_altitude', result)
            self.assertIn('average_altitude', result)
            self.assertIn('trend_slope_km_per_day', result)
            self.assertIn('trend_slope_m_per_day', result)
            self.assertIn('total_change', result)
    
    def test_analyze_pass_frequency(self):
        """Тест анализа частоты пролетов"""
        from src.iss_orbital_analysis import analyze_pass_frequency
        
        # Тестируем функцию анализа частоты пролетов
        result = analyze_pass_frequency(55.7558, 37.6173, days=7)  # Москва
        
        # Проверяем, что результат не None
        self.assertIsNotNone(result)
        
        # Проверяем наличие ключевых полей в результате
        if result is not None:
            self.assertIn('total_passes', result)
            self.assertIn('avg_passes_per_day', result)
            self.assertIn('std_passes_per_day', result)
            self.assertIn('max_passes_per_day', result)
            self.assertIn('min_passes_per_day', result)
            self.assertIn('most_active_day', result)
            self.assertIn('least_active_day', result)
            self.assertIn('passes_data', result)


def run_tests():
    """Запуск всех тестов"""
    # Создание test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавление всех тестов
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinateConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestOrbitalCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticsCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestNewFunctions))  # Добавляем новые тесты
    
    # Запуск тестов
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывод итоговой статистики
    print("\n" + "="*70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*70)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
