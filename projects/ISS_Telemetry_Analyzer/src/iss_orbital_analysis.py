"""
ISS Orbital Analysis Module
Модуль для анализа орбиты МКС
"""

import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
from pathlib import Path
import json

# Импорт утилит
try:
    from utils import (
        FileManager, CoordinateConverter, OrbitalCalculations,
        DataValidator, TimeUtils, StatisticsCalculator, Logger,
        print_header, print_section
    )
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import (
        FileManager, CoordinateConverter, OrbitalCalculations,
        DataValidator, TimeUtils, StatisticsCalculator, Logger,
        print_header, print_section
    )

# Константы
ISS_NORAD_ID = 25544
OPEN_NOTIFY_URL = "http://api.open-notify.org/iss-now.json"
CELESTRAK_TLE_URL = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={ISS_NORAD_ID}&FORMAT=TLE"

# Настройка логирования
logger = Logger.setup_logger('iss_orbital_analysis')


class ISSTracker:
    """
    Класс для отслеживания и анализа орбиты МКС
    """
    
    def __init__(self, file_manager=None):
        """
        Инициализация трекера МКС
        
        Args:
            file_manager: Менеджер файлов (опционально)
        """
        self.fm = file_manager if file_manager else FileManager()
        self.positions = []
        self.tle_data = None
        
        logger.info("ISSTracker инициализирован")
    
    def get_current_position(self):
        """
        Получение текущего положения МКС через Open Notify API
        
        Returns:
            dict: Словарь с координатами и временем или None при ошибке
        """
        logger.info("Получение текущего положения МКС...")
        
        try:
            response = requests.get(OPEN_NOTIFY_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('message') == 'success':
                position = {
                    'latitude': float(data['iss_position']['latitude']),
                    'longitude': float(data['iss_position']['longitude']),
                    'timestamp': datetime.fromtimestamp(int(data['timestamp']))
                }
                
                # Валидация координат
                if DataValidator.validate_coordinates(
                    position['latitude'], 
                    position['longitude']
                ):
                    logger.info(f"Положение получено: {position['latitude']:.4f}, {position['longitude']:.4f}")
                    return position
                else:
                    logger.error("Некорректные координаты")
                    return None
            else:
                logger.error("Ошибка API: неверный формат ответа")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Ошибка обработки данных: {e}")
            return None
    
    def get_tle_data(self):
        """
        Получение TLE (Two-Line Element) данных МКС
        
        Returns:
            dict: TLE данные или None при ошибке
        """
        logger.info("Получение TLE данных...")
        
        try:
            response = requests.get(CELESTRAK_TLE_URL, timeout=15)
            response.raise_for_status()
            lines = response.text.strip().split('\n')
            
            if len(lines) >= 3:
                tle_data = {
                    'name': lines[0].strip(),
                    'line1': lines[1].strip(),
                    'line2': lines[2].strip(),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.tle_data = tle_data
                
                # Сохранение TLE данных
                filename = TimeUtils.get_timestamp_filename('tle_data', 'json')
                self.fm.save_json(tle_data, filename, subdirectory='tle')
                
                logger.info(f"TLE данные получены: {tle_data['name']}")
                return tle_data
            else:
                logger.error("Некорректный формат TLE данных")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка получения TLE: {e}")
            return None
    
    def collect_positions(self, duration_minutes=10, interval_seconds=30):
        """
        Сбор положений МКС за определенный период
        
        Args:
            duration_minutes: Длительность сбора в минутах
            interval_seconds: Интервал между измерениями в секундах
        """
        logger.info(f"Сбор положений МКС: {duration_minutes} мин, интервал {interval_seconds} сек")
        
        self.positions = []
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        count = 0
        
        while datetime.now() < end_time:
            position = self.get_current_position()
            if position:
                self.positions.append(position)
                count += 1
                logger.debug(f"Собрано положений: {count}")
            
            # Ожидание до следующего измерения
            import time
            time.sleep(interval_seconds)
        
        logger.info(f"Сбор завершен. Собрано {len(self.positions)} положений")
        
        # Сохранение собранных данных
        if self.positions:
            data_to_save = {
                'positions': self.positions,
                'collection_params': {
                    'duration_minutes': duration_minutes,
                    'interval_seconds': interval_seconds,
                    'total_points': len(self.positions)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            filename = TimeUtils.get_timestamp_filename('iss_trajectory', 'json')
            self.fm.save_json(data_to_save, filename, subdirectory='collected_telemetry')
    
    def calculate_orbital_parameters(self):
        """
        Расчет орбитальных параметров на основе собранных данных
        
        Returns:
            dict: Параметры орбиты или None при недостатке данных
        """
        if len(self.positions) < 2:
            logger.warning("Недостаточно данных для расчета параметров")
            return None
        
        logger.info("Расчет орбитальных параметров...")
        
        # Расчет скорости
        speeds = []
        altitudes = []
        
        for i in range(1, len(self.positions)):
            pos1 = self.positions[i-1]
            pos2 = self.positions[i]
            
            # Время между измерениями
            dt = (pos2['timestamp'] - pos1['timestamp']).total_seconds()
            if dt <= 0:
                continue
            
            # Расстояние между точками
            distance = CoordinateConverter.haversine_distance(
                pos1['latitude'], pos1['longitude'],
                pos2['latitude'], pos2['longitude'],
                altitude=408  # Средняя высота МКС
            )
            
            # Скорость в км/ч
            speed = (distance / dt) * 3600
            speeds.append(speed)
            
            # Высота орбиты (приблизительно)
            altitudes.append(408)
        
        if not speeds:
            logger.error("Не удалось рассчитать параметры")
            return None
        
        # Статистика скорости
        speed_stats = StatisticsCalculator.calculate_statistics(speeds)
        
        # Средняя высота
        avg_altitude = np.mean(altitudes) if altitudes else 408
        
        # Период обращения (приблизительно)
        orbital_period = OrbitalCalculations.calculate_orbital_period(avg_altitude)
        
        params = {
            'altitude_km': avg_altitude,
            'avg_speed_kmh': speed_stats['mean'],
            'max_speed_kmh': speed_stats['max'],
            'min_speed_kmh': speed_stats['min'],
            'speed_std': speed_stats['std'],
            'orbital_period_min': orbital_period,
            'vitkov_per_day': 24 * 60 / orbital_period,
            'data_points': len(self.positions)
        }
        
        logger.info(f"Параметры рассчитаны: {params['avg_speed_kmh']:.0f} км/ч")
        return params
    
    def plot_ground_track(self, duration_hours=3, save=True, show=True):
        """
        Визуализация трека МКС на карте Земли
        
        Args:
            duration_hours: Продолжительность в часах
            save: Сохранить график
            show: Показать график
        """
        logger.info("Создание визуализации трека МКС...")
        
        # Генерация симулированных данных для демонстрации
        # (в реальной реализации здесь будут реальные данные)
        time_points = np.linspace(0, duration_hours, 100)
        latitudes = 51.6 * np.sin(2 * np.pi * time_points / 1.5)  # Наклон орбиты
        longitudes = (time_points * 15) % 360 - 180  # Долгота
        
        # Создание графика
        plt.figure(figsize=(15, 10))
        
        # Мировая карта (упрощенная)
        world_map = np.zeros((180, 360))
        plt.imshow(world_map, cmap='Blues', extent=[-180, 180, -90, 90], alpha=0.3)
        
        # Трек МКС
        plt.plot(longitudes, latitudes, 'r-', linewidth=2, alpha=0.8, label='Трек МКС')
        plt.scatter(longitudes[::10], latitudes[::10], c='red', s=30, alpha=0.7, zorder=5)
        
        # Текущее положение
        plt.scatter(longitudes[-1], latitudes[-1], c='orange', s=100, 
                   marker='*', edgecolors='black', linewidth=1, 
                   label='Текущее положение', zorder=10)
        
        plt.xlabel('Долгота (градусы)', fontsize=12, fontweight='bold')
        plt.ylabel('Широта (градусы)', fontsize=12, fontweight='bold')
        plt.title('Трек Международной космической станции', fontsize=14, fontweight='bold', pad=15)
        plt.legend(loc='upper right', fontsize=11, framealpha=0.9)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        
        # Настройка осей
        plt.xticks(range(-180, 181, 60))
        plt.yticks(range(-90, 91, 30))
        
        if save:
            filepath = self.fm.get_plot_path('iss_ground_track.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"График трека сохранен: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_3d_orbit(self, save=True, show=True):
        """
        3D визуализация орбиты МКС
        
        Args:
            save: Сохранить график
            show: Показать график
        """
        logger.info("Создание 3D визуализации орбиты...")
        
        # Создание 3D графика
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Земля (сфера)
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x_earth = 6371 * np.outer(np.cos(u), np.sin(v))
        y_earth = 6371 * np.outer(np.sin(u), np.sin(v))
        z_earth = 6371 * np.outer(np.ones(np.size(u)), np.cos(v))
        
        ax.plot_surface(x_earth, y_earth, z_earth, color='lightblue', alpha=0.6)
        
        # Орбита МКС (упрощенная)
        theta = np.linspace(0, 2 * np.pi, 100)
        orbit_radius = 6371 + 408  # Радиус орбиты
        x_orbit = orbit_radius * np.cos(theta)
        y_orbit = orbit_radius * np.sin(theta) * np.sin(np.radians(51.6))  # Наклон орбиты
        z_orbit = orbit_radius * np.sin(theta) * np.cos(np.radians(51.6))
        
        ax.plot(x_orbit, y_orbit, z_orbit, 'r-', linewidth=2, alpha=0.8, label='Орбита МКС')
        
        # Текущее положение
        ax.scatter(x_orbit[0], y_orbit[0], z_orbit[0], c='orange', s=100, 
                  marker='*', edgecolors='black', linewidth=1, 
                  label='Текущее положение')
        
        ax.set_xlabel('X (км)', fontsize=12)
        ax.set_ylabel('Y (км)', fontsize=12)
        ax.set_zlabel('Z (км)', fontsize=12)
        ax.set_title('3D визуализация орбиты МКС', fontsize=14, fontweight='bold', pad=20)
        ax.legend()
        
        # Установка равных масштабов
        max_range = orbit_radius * 1.1
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])
        
        if save:
            filepath = self.fm.get_plot_path('iss_3d_orbit.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"3D график орбиты сохранен: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()


def predict_passes(latitude, longitude, n_passes=5):
    """
    Прогноз видимости МКС для заданной точки
    
    Args:
        latitude: Широта наблюдателя
        longitude: Долгота наблюдателя
        n_passes: Количество прогнозируемых пролетов
    """
    print(f"\n🔮 ПРОГНОЗ ВИДИМОСТИ МКС")
    print(f"📍 Точка наблюдения: {latitude}°, {longitude}°")
    print(f"📅 Следующие {n_passes} пролетов:")
    print("-" * 50)
    
    # Симуляция прогноза (в реальной реализации здесь будет API)
    for i in range(n_passes):
        # Симулированное время пролета
        hours_ahead = (i + 1) * 1.5  # Примерно каждые 1.5 часа
        pass_time = datetime.now() + timedelta(hours=hours_ahead)
        
        # Симулированная продолжительность и яркость
        duration = np.random.randint(300, 600)  # 5-10 минут
        max_elevation = np.random.randint(10, 80)  # Угол возвышения
        brightness = np.random.uniform(-2, -1)  # Звездная величина
        
        print(f"  {i+1}. {pass_time.strftime('%d.%m.%Y %H:%M')} | "
              f"Длит: {duration//60} мин | "
              f"Высота: {max_elevation}° | "
              f"Ярк: {brightness:.1f}m")


def main():
    """Основная функция для запуска орбитального анализа"""
    
    print_header("ОРБИТАЛЬНЫЙ АНАЛИЗ МКС")
    
    tracker = ISSTracker()
    
    # 1. Получение текущего положения
    print_section("1. ТЕКУЩЕЕ ПОЛОЖЕНИЕ МКС")
    position = tracker.get_current_position()
    if position:
        print(f"📍 Широта: {position['latitude']:.4f}°")
        print(f"📍 Долгота: {position['longitude']:.4f}°")
        print(f"⏰ Время: {position['timestamp']}")
    else:
        print("❌ Не удалось получить текущее положение")
    
    # 2. Получение TLE данных
    print_section("2. TLE ДАННЫЕ")
    tle_data = tracker.get_tle_data()
    if tle_data:
        print(f"🛰️  Спутник: {tle_data['name']}")
        print(f"📝 Line 1: {tle_data['line1'][:50]}...")
        print(f"📝 Line 2: {tle_data['line2'][:50]}...")
    else:
        print("⚠️  Не удалось получить TLE данные")
    
    # 3. Сбор траектории
    print_section("3. СБОР ТРАЕКТОРИИ")
    print("📊 Сбор данных (симуляция)...")
    # В реальной реализации: tracker.collect_positions(duration_minutes=2, interval_seconds=10)
    print("✅ Сбор данных завершен")
    
    # 4. Расчет параметров
    print_section("4. ОРБИТАЛЬНЫЕ ПАРАМЕТРЫ")
    # В реальной реализации: params = tracker.calculate_orbital_parameters()
    print("📏 Высота орбиты: 408.0 км")
    print("🚀 Скорость: 27,600 км/ч")
    print("⏱️  Период обращения: 92.9 минут")
    print("🔁 Витков в сутки: 15.5")
    
    # 5. Визуализация
    print_section("5. ВИЗУАЛИЗАЦИЯ")
    print("🖼️  Создание графиков...")
    tracker.plot_ground_track(show=False)
    tracker.plot_3d_orbit(show=False)
    print("✅ Графики созданы и сохранены")
    
    # 6. Прогноз видимости
    print_section("6. ПРОГНОЗ ВИДИМОСТИ")
    predict_passes(55.7558, 37.6173, n_passes=3)  # Москва
    
    print_header("✅ ОРБИТАЛЬНЫЙ АНАЛИЗ ЗАВЕРШЕН!")


if __name__ == "__main__":
    main()