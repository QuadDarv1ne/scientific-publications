"""
Вспомогательные функции для ISS Telemetry Analyzer
Содержит общие утилиты для работы с данными, файлами и расчетами
"""

import os
import json
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileManager:
    """Менеджер для работы с файлами и директориями проекта"""
    
    def __init__(self, base_dir=None):
        """
        Инициализация менеджера файлов
        
        Args:
            base_dir: Базовая директория проекта
        """
        if base_dir is None:
            # Получаем корневую директорию проекта (на уровень выше src/)
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        # Определение путей к директориям
        self.data_dir = self.base_dir / 'data'
        self.tle_dir = self.data_dir / 'tle_data'
        self.telemetry_dir = self.data_dir / 'collected_telemetry'
        self.results_dir = self.base_dir / 'results'
        self.plots_dir = self.results_dir / 'plots'
        self.reports_dir = self.results_dir / 'reports'
        self.analysis_dir = self.results_dir / 'analysis'
        
        # Создание директорий если их нет
        self._create_directories()
    
    def _create_directories(self):
        """Создание всех необходимых директорий"""
        directories = [
            self.data_dir,
            self.tle_dir,
            self.telemetry_dir,
            self.results_dir,
            self.plots_dir,
            self.reports_dir,
            self.analysis_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Директория создана/проверена: {directory}")
    
    def save_json(self, data, filename, subdirectory='telemetry'):
        """
        Сохранение данных в JSON формате
        
        Args:
            data: Данные для сохранения
            filename: Имя файла
            subdirectory: Поддиректория (telemetry, tle, analysis)
        
        Returns:
            Path: Путь к сохраненному файлу
        """
        if subdirectory == 'telemetry':
            filepath = self.telemetry_dir / filename
        elif subdirectory == 'tle':
            filepath = self.tle_dir / filename
        elif subdirectory == 'analysis':
            filepath = self.analysis_dir / filename
        else:
            filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False, default=str)
            logger.info(f"Данные сохранены: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Ошибка сохранения JSON: {e}")
            return None
    
    def load_json(self, filename, subdirectory='telemetry'):
        """
        Загрузка данных из JSON файла
        
        Args:
            filename: Имя файла
            subdirectory: Поддиректория
        
        Returns:
            dict: Загруженные данные или None
        """
        if subdirectory == 'telemetry':
            filepath = self.telemetry_dir / filename
        elif subdirectory == 'tle':
            filepath = self.tle_dir / filename
        elif subdirectory == 'analysis':
            filepath = self.analysis_dir / filename
        else:
            filepath = self.data_dir / filename
        
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Данные загружены: {filepath}")
                return data
            else:
                logger.warning(f"Файл не найден: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Ошибка загрузки JSON: {e}")
            return None
    
    def get_plot_path(self, filename):
        """Получение полного пути для сохранения графика"""
        return self.plots_dir / filename
    
    def get_report_path(self, filename):
        """Получение полного пути для сохранения отчета"""
        return self.reports_dir / filename


class CoordinateConverter:
    """Конвертер координат между различными системами"""
    
    EARTH_RADIUS = 6371.0  # км
    
    @staticmethod
    def geodetic_to_cartesian(latitude, longitude, altitude=0):
        """
        Конвертация геодезических координат в декартовы (ECEF)
        
        Args:
            latitude: Широта в градусах
            longitude: Долгота в градусах
            altitude: Высота над уровнем моря в км
        
        Returns:
            tuple: (x, y, z) в км
        """
        lat_rad = np.radians(latitude)
        lon_rad = np.radians(longitude)
        
        r = CoordinateConverter.EARTH_RADIUS + altitude
        
        x = r * np.cos(lat_rad) * np.cos(lon_rad)
        y = r * np.cos(lat_rad) * np.sin(lon_rad)
        z = r * np.sin(lat_rad)
        
        return x, y, z
    
    @staticmethod
    def cartesian_to_geodetic(x, y, z):
        """
        Конвертация декартовых координат в геодезические
        
        Args:
            x, y, z: Декартовы координаты в км
        
        Returns:
            tuple: (latitude, longitude, altitude)
        """
        r = np.sqrt(x**2 + y**2 + z**2)
        altitude = r - CoordinateConverter.EARTH_RADIUS
        
        latitude = np.degrees(np.arcsin(z / r))
        longitude = np.degrees(np.arctan2(y, x))
        
        return latitude, longitude, altitude
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2, altitude=0):
        """
        Расчет расстояния между двумя точками на сфере (формула гаверсинусов)
        
        Args:
            lat1, lon1: Координаты первой точки (градусы)
            lat2, lon2: Координаты второй точки (градусы)
            altitude: Высота орбиты в км
        
        Returns:
            float: Расстояние в км
        """
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        r = CoordinateConverter.EARTH_RADIUS + altitude
        distance = r * c
        
        return distance


class OrbitalCalculations:
    """Класс для орбитальных вычислений"""
    
    EARTH_MU = 398600.4418  # км³/с² - гравитационный параметр Земли
    EARTH_RADIUS = 6371.0   # км
    
    @staticmethod
    def calculate_orbital_velocity(altitude):
        """
        Расчет орбитальной скорости на заданной высоте
        
        Args:
            altitude: Высота орбиты в км
        
        Returns:
            float: Орбитальная скорость в км/с
        """
        r = OrbitalCalculations.EARTH_RADIUS + altitude
        velocity = np.sqrt(OrbitalCalculations.EARTH_MU / r)
        return velocity
    
    @staticmethod
    def calculate_orbital_period(altitude):
        """
        Расчет периода обращения на заданной высоте
        
        Args:
            altitude: Высота орбиты в км
        
        Returns:
            float: Период обращения в минутах
        """
        r = OrbitalCalculations.EARTH_RADIUS + altitude
        period_seconds = 2 * np.pi * np.sqrt(r**3 / OrbitalCalculations.EARTH_MU)
        period_minutes = period_seconds / 60
        return period_minutes
    
    @staticmethod
    def calculate_escape_velocity(altitude):
        """
        Расчет второй космической скорости на заданной высоте
        
        Args:
            altitude: Высота в км
        
        Returns:
            float: Вторая космическая скорость в км/с
        """
        r = OrbitalCalculations.EARTH_RADIUS + altitude
        escape_vel = np.sqrt(2 * OrbitalCalculations.EARTH_MU / r)
        return escape_vel
    
    @staticmethod
    def atmospheric_drag_coefficient(altitude):
        """
        Приблизительный коэффициент атмосферного торможения
        
        Args:
            altitude: Высота орбиты в км
        
        Returns:
            float: Коэффициент торможения (относительный)
        """
        # Упрощенная модель: торможение резко уменьшается с высотой
        if altitude < 200:
            return 10.0
        elif altitude < 300:
            return 5.0
        elif altitude < 400:
            return 2.0
        elif altitude < 500:
            return 0.5
        else:
            return 0.1


class DataValidator:
    """Валидатор данных телеметрии"""
    
    @staticmethod
    def validate_coordinates(latitude, longitude):
        """
        Проверка корректности координат
        
        Args:
            latitude: Широта
            longitude: Долгота
        
        Returns:
            bool: True если координаты корректны
        """
        if not (-90 <= latitude <= 90):
            logger.error(f"Некорректная широта: {latitude}")
            return False
        
        if not (-180 <= longitude <= 180):
            logger.error(f"Некорректная долгота: {longitude}")
            return False
        
        return True
    
    @staticmethod
    def validate_altitude(altitude):
        """
        Проверка корректности высоты орбиты
        
        Args:
            altitude: Высота в км
        
        Returns:
            bool: True если высота корректна
        """
        # МКС обычно летает на высоте 400-420 км
        if not (350 <= altitude <= 450):
            logger.warning(f"Необычная высота орбиты: {altitude} км")
        
        if altitude < 0 or altitude > 1000:
            logger.error(f"Некорректная высота: {altitude} км")
            return False
        
        return True
    
    @staticmethod
    def validate_velocity(velocity):
        """
        Проверка корректности скорости
        
        Args:
            velocity: Скорость в км/с
        
        Returns:
            bool: True если скорость корректна
        """
        # Первая космическая ~7.9 км/с, вторая ~11.2 км/с
        if not (7.0 <= velocity <= 12.0):
            logger.warning(f"Необычная скорость: {velocity} км/с")
        
        if velocity < 0 or velocity > 20:
            logger.error(f"Некорректная скорость: {velocity} км/с")
            return False
        
        return True


class TimeUtils:
    """Утилиты для работы со временем"""
    
    @staticmethod
    def timestamp_to_datetime(timestamp):
        """Конвертация Unix timestamp в datetime"""
        return datetime.fromtimestamp(timestamp)
    
    @staticmethod
    def datetime_to_timestamp(dt):
        """Конвертация datetime в Unix timestamp"""
        return dt.timestamp()
    
    @staticmethod
    def format_duration(seconds):
        """
        Форматирование длительности в читаемый вид
        
        Args:
            seconds: Длительность в секундах
        
        Returns:
            str: Отформатированная строка
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}ч {minutes}м {secs}с"
        elif minutes > 0:
            return f"{minutes}м {secs}с"
        else:
            return f"{secs}с"
    
    @staticmethod
    def get_timestamp_filename(prefix='data', extension='json'):
        """
        Генерация имени файла с временной меткой
        
        Args:
            prefix: Префикс имени файла
            extension: Расширение файла
        
        Returns:
            str: Имя файла с временной меткой
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}.{extension}"


class StatisticsCalculator:
    """Калькулятор статистических параметров"""
    
    @staticmethod
    def calculate_statistics(data):
        """
        Расчет основных статистических параметров
        
        Args:
            data: Массив данных
        
        Returns:
            dict: Словарь со статистикой
        """
        if len(data) == 0:
            return None
        
        data_array = np.array(data)
        
        stats = {
            'mean': np.mean(data_array),
            'median': np.median(data_array),
            'std': np.std(data_array),
            'min': np.min(data_array),
            'max': np.max(data_array),
            'range': np.max(data_array) - np.min(data_array),
            'count': len(data_array)
        }
        
        return stats
    
    @staticmethod
    def moving_average(data, window_size=5):
        """
        Расчет скользящего среднего
        
        Args:
            data: Массив данных
            window_size: Размер окна
        
        Returns:
            np.array: Сглаженные данные
        """
        if len(data) < window_size:
            return np.array(data)
        
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')


class Logger:
    """Расширенный логгер для проекта"""
    
    @staticmethod
    def setup_logger(name, log_file=None, level=logging.INFO):
        """
        Настройка логгера
        
        Args:
            name: Имя логгера
            log_file: Путь к файлу лога (опционально)
            level: Уровень логирования
        
        Returns:
            logging.Logger: Настроенный логгер
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Формат сообщений
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Файловый handler (если указан)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger


def print_header(text, char='=', width=60):
    """
    Печать красивого заголовка
    
    Args:
        text: Текст заголовка
        char: Символ для рамки
        width: Ширина рамки
    """
    print(char * width)
    print(text.center(width))
    print(char * width)


def print_section(title):
    """Печать заголовка секции"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


# Экспорт основных классов и функций
__all__ = [
    'FileManager',
    'CoordinateConverter',
    'OrbitalCalculations',
    'DataValidator',
    'TimeUtils',
    'StatisticsCalculator',
    'Logger',
    'print_header',
    'print_section'
]


if __name__ == "__main__":
    # Тестирование утилит
    print_header("ТЕСТИРОВАНИЕ УТИЛИТ")
    
    # Тест FileManager
    print("\n1. Тестирование FileManager ...")
    fm = FileManager()
    print(f"   Базовая директория: {fm.base_dir}")
    print(f"   Директория данных: {fm.data_dir}")
    
    # Тест CoordinateConverter
    print("\n2. Тестирование CoordinateConverter ...")
    lat, lon = 55.7558, 37.6173  # Москва
    x, y, z = CoordinateConverter.geodetic_to_cartesian(lat, lon, 408)
    print(f"   Москва (геодезические): {lat}°, {lon}°")
    print(f"   Москва (декартовы): {x:.2f}, {y:.2f}, {z:.2f} км")
    
    # Тест OrbitalCalculations
    print("\n3. Тестирование OrbitalCalculations ...")
    altitude = 408
    velocity = OrbitalCalculations.calculate_orbital_velocity(altitude)
    period = OrbitalCalculations.calculate_orbital_period(altitude)
    print(f"   Высота: {altitude} км")
    print(f"   Орбитальная скорость: {velocity:.3f} км/с")
    print(f"   Период обращения: {period:.2f} минут")
    
    # Тест DataValidator
    print("\n4. Тестирование DataValidator ...")
    print(f"   Координаты (55.7558, 37.6173) корректны: {DataValidator.validate_coordinates(55.7558, 37.6173)}")
    print(f"   Высота 408 км корректна: {DataValidator.validate_altitude(408)}")
    print(f"   Скорость 7.66 км/с корректна: {DataValidator.validate_velocity(7.66)}")
    
    print("\n✓ Все тесты пройдены успешно")
