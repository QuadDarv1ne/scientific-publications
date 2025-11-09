"""
Unit tests for ISS Telemetry Analyzer Utilities
Тесты для вспомогательных функций анализатора телеметрии МКС
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import numpy as np
import os
import json
import tempfile
import shutil

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils import (
    FileManager, CoordinateConverter, OrbitalCalculations,
    DataValidator, TimeUtils, StatisticsCalculator, Logger
)


class TestFileManager(unittest.TestCase):
    """Тесты для менеджера файлов"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создание временной директории для тестов
        self.test_dir = tempfile.mkdtemp()
        self.fm = FileManager(self.test_dir)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаление временной директории
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init(self):
        """Тест инициализации менеджера файлов"""
        self.assertIsInstance(self.fm, FileManager)
        self.assertTrue(os.path.exists(self.fm.base_dir))
        self.assertTrue(os.path.exists(self.fm.data_dir))
        self.assertTrue(os.path.exists(self.fm.results_dir))
    
    def test_save_load_json(self):
        """Тест сохранения и загрузки JSON данных"""
        test_data = {
            'test': 'data',
            'number': 42,
            'list': [1, 2, 3]
        }
        
        # Сохранение данных
        filename = 'test_data.json'
        filepath = self.fm.save_json(test_data, filename, subdirectory='telemetry')
        
        # Проверка что файл был создан
        if filepath is not None:
            self.assertTrue(os.path.exists(filepath))
            
            # Загрузка данных
            loaded_data = self.fm.load_json(filename, subdirectory='telemetry')
            
            self.assertIsNotNone(loaded_data)
            self.assertEqual(test_data, loaded_data)
        else:
            self.fail("Failed to save JSON data")
    
    def test_load_nonexistent_json(self):
        """Тест загрузки несуществующего файла"""
        loaded_data = self.fm.load_json('nonexistent.json', subdirectory='telemetry')
        self.assertIsNone(loaded_data)


class TestCoordinateConverter(unittest.TestCase):
    """Тесты для конвертера координат"""
    
    def test_geodetic_to_cartesian(self):
        """Тест конвертации геодезических координат в декартовы"""
        # Тест на уровне моря
        lat, lon, alt = 0, 0, 0
        x, y, z = CoordinateConverter.geodetic_to_cartesian(lat, lon, alt)
        
        # Проверка что точка на экваторе и нулевом меридиане
        # находится на расстоянии радиуса Земли от центра
        r = np.sqrt(x**2 + y**2 + z**2)
        self.assertAlmostEqual(r, CoordinateConverter.EARTH_RADIUS, delta=1.0)
    
    def test_cartesian_to_geodetic(self):
        """Тест конвертации декартовых координат в геодезические"""
        # Конвертация туда и обратно
        lat1, lon1, alt1 = 45, 30, 408  # МКС на орбите (целые числа)
        x, y, z = CoordinateConverter.geodetic_to_cartesian(lat1, lon1, alt1)
        lat2, lon2, alt2 = CoordinateConverter.cartesian_to_geodetic(x, y, z)
        
        # Проверка что получили исходные координаты
        self.assertAlmostEqual(lat1, lat2, delta=0.1)
        self.assertAlmostEqual(lon1, lon2, delta=0.1)
        self.assertAlmostEqual(alt1, alt2, delta=1.0)
    
    def test_haversine_distance(self):
        """Тест расчета расстояния между точками"""
        # Расстояние от точки до самой себя должно быть 0
        lat, lon = 55.7558, 37.6173  # Москва
        distance = CoordinateConverter.haversine_distance(lat, lon, lat, lon)
        self.assertAlmostEqual(distance, 0, delta=0.01)


class TestOrbitalCalculations(unittest.TestCase):
    """Тесты для орбитальных вычислений"""
    
    def test_orbital_velocity(self):
        """Тест расчета орбитальной скорости"""
        altitude = 408  # МКС
        velocity = OrbitalCalculations.calculate_orbital_velocity(altitude)
        
        # Первая космическая скорость для МКС ~7.66 км/с
        self.assertGreater(velocity, 7.5)
        self.assertLess(velocity, 8.0)
    
    def test_orbital_period(self):
        """Тест расчета периода обращения"""
        altitude = 408  # МКС
        period = OrbitalCalculations.calculate_orbital_period(altitude)
        
        # Период обращения МКС ~93 минуты
        self.assertGreater(period, 90)
        self.assertLess(period, 95)
    
    def test_atmospheric_drag(self):
        """Тест коэффициента атмосферного торможения"""
        # Чем выше орбита, тем меньше торможение
        drag_low = OrbitalCalculations.atmospheric_drag_coefficient(200)
        drag_high = OrbitalCalculations.atmospheric_drag_coefficient(500)
        
        self.assertGreaterEqual(drag_low, drag_high)


class TestDataValidator(unittest.TestCase):
    """Тесты для валидатора данных"""
    
    def test_valid_coordinates(self):
        """Тест валидных координат"""
        self.assertTrue(DataValidator.validate_coordinates(0, 0))
        self.assertTrue(DataValidator.validate_coordinates(45, 30))
        self.assertTrue(DataValidator.validate_coordinates(-90, -180))
        self.assertTrue(DataValidator.validate_coordinates(90, 180))
    
    def test_invalid_coordinates(self):
        """Тест невалидных координат"""
        self.assertFalse(DataValidator.validate_coordinates(91, 0))
        self.assertFalse(DataValidator.validate_coordinates(0, 181))
        self.assertFalse(DataValidator.validate_coordinates(-91, -181))
    
    def test_valid_altitude(self):
        """Тест валидной высоты"""
        self.assertTrue(DataValidator.validate_altitude(408))
        self.assertTrue(DataValidator.validate_altitude(400))
        self.assertTrue(DataValidator.validate_altitude(420))
    
    def test_invalid_altitude(self):
        """Тест невалидной высоты"""
        self.assertFalse(DataValidator.validate_altitude(-10))
        self.assertFalse(DataValidator.validate_altitude(2000))


class TestTimeUtils(unittest.TestCase):
    """Тесты для утилит работы со временем"""
    
    def test_timestamp_conversion(self):
        """Тест конвертации timestamp"""
        dt = datetime.now()
        timestamp = TimeUtils.datetime_to_timestamp(dt)
        dt2 = TimeUtils.timestamp_to_datetime(timestamp)
        
        # Проверка что время не сильно изменилось
        self.assertAlmostEqual(
            dt.timestamp(), 
            dt2.timestamp(), 
            delta=1.0
        )
    
    def test_format_duration(self):
        """Тест форматирования длительности"""
        # Тест секунд
        duration = TimeUtils.format_duration(45)
        self.assertIn('45с', duration)
        
        # Тест минут
        duration = TimeUtils.format_duration(125)
        self.assertIn('2м', duration)
        self.assertIn('5с', duration)
        
        # Тест часов
        duration = TimeUtils.format_duration(3665)
        self.assertIn('1ч', duration)
        self.assertIn('1м', duration)
        self.assertIn('5с', duration)


class TestStatisticsCalculator(unittest.TestCase):
    """Тесты для калькулятора статистики"""
    
    def test_basic_statistics(self):
        """Тест базовой статистики"""
        data = [1, 2, 3, 4, 5]
        stats = StatisticsCalculator.calculate_statistics(data)
        
        # Проверка что статистика не None
        self.assertIsNotNone(stats)
        
        if stats is not None:
            self.assertEqual(stats['mean'], 3.0)
            self.assertEqual(stats['median'], 3.0)
            self.assertEqual(stats['min'], 1)
            self.assertEqual(stats['max'], 5)
            self.assertEqual(stats['count'], 5)
    
    def test_empty_data(self):
        """Тест пустых данных"""
        stats = StatisticsCalculator.calculate_statistics([])
        self.assertIsNone(stats)
    
    def test_moving_average(self):
        """Тест скользящего среднего"""
        data = [1, 2, 3, 4, 5]
        smoothed = StatisticsCalculator.moving_average(data, window_size=3)
        
        # Проверка что результат короче исходных данных
        self.assertLess(len(smoothed), len(data))
        
        # Проверка значений
        self.assertAlmostEqual(smoothed[0], 2.0, delta=0.1)


class TestLogger(unittest.TestCase):
    """Тесты для логгера"""
    
    def test_setup_logger(self):
        """Тест настройки логгера"""
        logger = Logger.setup_logger('test_logger')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'test_logger')


def run_tests():
    """Запуск всех тестов"""
    # Создание test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавление всех тестов
    suite.addTests(loader.loadTestsFromTestCase(TestFileManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinateConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestOrbitalCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticsCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    
    # Запуск тестов
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывод итоговой статистики
    print("\n" + "="*70)
    print("ИТОГИ ТЕСТИРОВАНИЯ ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ")
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