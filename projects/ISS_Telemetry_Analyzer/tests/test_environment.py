"""
Unit tests for ISS Environment Analysis Module
Тесты для модуля анализа условий окружающей среды МКС
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils import (
    FileManager, StatisticsCalculator, TimeUtils
)
from iss_environment_analysis import ISSEnvironmentAnalyzer


class TestISSEnvironmentAnalyzer(unittest.TestCase):
    """Тесты для анализатора условий окружающей среды МКС"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.analyzer = ISSEnvironmentAnalyzer()
    
    def test_init(self):
        """Тест инициализации анализатора"""
        self.assertIsInstance(self.analyzer, ISSEnvironmentAnalyzer)
        self.assertIsNotNone(self.analyzer.fm)
    
    def test_simulate_temperature_profile(self):
        """Тест симуляции температурного профиля"""
        time_h, internal_temp, external_temp = self.analyzer.simulate_temperature_profile(50, 12)
        
        # Проверка размеров массивов
        self.assertEqual(len(time_h), 50)
        self.assertEqual(len(internal_temp), 50)
        self.assertEqual(len(external_temp), 50)
        
        # Проверка диапазонов температур
        self.assertTrue(np.all(internal_temp >= 18))
        self.assertTrue(np.all(internal_temp <= 27))
        
        # Проверка что время начинается с 0
        self.assertEqual(time_h[0], 0)
    
    def test_simulate_radiation_levels(self):
        """Тест симуляции уровней радиации"""
        time_h, radiation = self.analyzer.simulate_radiation_levels(50, 12)
        
        # Проверка размеров массивов
        self.assertEqual(len(time_h), 50)
        self.assertEqual(len(radiation), 50)
        
        # Проверка что уровни радиации неотрицательные
        self.assertTrue(np.all(radiation >= 0))
        
        # Проверка что время начинается с 0
        self.assertEqual(time_h[0], 0)
    
    def test_simulate_altitude_profile(self):
        """Тест симуляции профиля высоты"""
        time_h, altitude = self.analyzer.simulate_altitude_profile(50, 12)
        
        # Проверка размеров массивов
        self.assertEqual(len(time_h), 50)
        self.assertEqual(len(altitude), 50)
        
        # Проверка что время начинается с 0
        self.assertEqual(time_h[0], 0)
    
    def test_statistics_calculator(self):
        """Тест калькулятора статистики"""
        # Тест на нормальных данных
        data = [1, 2, 3, 4, 5]
        stats = StatisticsCalculator.calculate_statistics(data)
        
        # Проверка что stats не None
        self.assertIsNotNone(stats)
        
        if stats is not None:
            self.assertEqual(stats['mean'], 3.0)
            self.assertEqual(stats['median'], 3.0)
            self.assertEqual(stats['min'], 1)
            self.assertEqual(stats['max'], 5)
        
        # Тест на пустых данных
        empty_stats = StatisticsCalculator.calculate_statistics([])
        self.assertIsNone(empty_stats)
    
    def test_time_utils(self):
        """Тест утилит работы со временем"""
        # Тест форматирования длительности
        duration_str = TimeUtils.format_duration(3665)  # 1ч 1м 5с
        self.assertIn('1ч', duration_str)
        self.assertIn('1м', duration_str)
        self.assertIn('5с', duration_str)
        
        # Тест генерации имени файла
        filename = TimeUtils.get_timestamp_filename('test', 'txt')
        self.assertTrue(filename.startswith('test_'))
        self.assertTrue(filename.endswith('.txt'))


def run_tests():
    """Запуск всех тестов"""
    # Создание test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавление тестов
    suite.addTests(loader.loadTestsFromTestCase(TestISSEnvironmentAnalyzer))
    
    # Запуск тестов
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывод итоговой статистики
    print("\n" + "="*70)
    print("ИТОГИ ТЕСТИРОВАНИЯ МОДУЛЯ ОКРУЖАЮЩЕЙ СРЕДЫ")
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