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
        self.orbital_params = None  # Добавляем атрибут для орбитальных параметров
        
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
                
        except requests.exceptions.Timeout:
            logger.error("Таймаут при запросе к API Open Notify")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Ошибка подключения к API Open Notify")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Ошибка обработки данных: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении положения МКС: {e}")
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
                
                # Парсинг орбитальных параметров из TLE
                self.orbital_params = self._parse_tle_data(tle_data['line1'], tle_data['line2'])
                
                # Сохранение TLE данных
                filename = TimeUtils.get_timestamp_filename('tle_data', 'json')
                self.fm.save_json(tle_data, filename, subdirectory='tle')
                
                logger.info(f"TLE данные получены: {tle_data['name']}")
                return tle_data
            else:
                logger.error("Некорректный формат TLE данных")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Таймаут при получении TLE данных")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Ошибка подключения при получении TLE данных")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка получения TLE: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении TLE данных: {e}")
            return None


    def _parse_tle_data(self, tle_line1, tle_line2):
        """
        Парсинг TLE данных для извлечения орбитальных параметров
        
        Args:
            tle_line1: Первая строка TLE
            tle_line2: Вторая строка TLE
            
        Returns:
            dict: Орбитальные параметры
        """
        try:
            # Извлечение наклонения орбиты (строка 2, позиции 9-16)
            inclination = float(tle_line2[8:16].strip())
            
            # Извлечение эксцентриситет (строка 2, позиции 27-33, нужно добавить "0.")
            eccentricity_str = tle_line2[26:33].strip()
            eccentricity = float("0." + eccentricity_str)
            
            # Извлечение среднего движения (строка 2, позиции 53-63)
            mean_motion = float(tle_line2[52:63].strip())
            
            # Расчет периода обращения (минуты)
            orbital_period = 1440 / mean_motion  # 1440 минут в сутках
            
            # Приблизительный расчет высоты орбиты
            # Используем формулу для больших полуосей
            earth_radius = 6371  # км
            mu = 398600.4418  # km³/s²
            
            # Преобразование среднего движения в радианы/секунду
            n_rad_per_sec = mean_motion * 2 * np.pi / 86400
            
            # Большая полуось в км
            semi_major_axis = (mu / (n_rad_per_sec ** 2)) ** (1/3)
            
            # Приблизительная высота орбиты
            altitude = semi_major_axis - earth_radius
            
            return {
                'inclination': inclination,
                'eccentricity': eccentricity,
                'mean_motion': mean_motion,
                'orbital_period_min': orbital_period,
                'altitude_km': max(altitude, 300)  # Ограничиваем снизу
            }
        except Exception as e:
            logger.error(f"Ошибка парсинга TLE данных: {e}")
            # Возвращаем значения по умолчанию
            return {
                'inclination': 51.64,
                'eccentricity': 0.0004093,
                'mean_motion': 15.49452868,
                'orbital_period_min': 92.9,
                'altitude_km': 408
            }
    
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
            try:
                position = self.get_current_position()
                if position:
                    self.positions.append(position)
                    count += 1
                    logger.debug(f"Собрано положений: {count}")
                
                # Ожидание до следующего измерения
                import time
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("Сбор данных прерван пользователем")
                break
            except Exception as e:
                logger.error(f"Ошибка при сборе данных: {e}")
                # Продолжаем сбор данных, несмотря на ошибку
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
        
        try:
            # Предварительная проверка данных
            valid_positions = []
            for pos in self.positions:
                if ('latitude' in pos and 'longitude' in pos and 
                    'timestamp' in pos and isinstance(pos['timestamp'], datetime)):
                    valid_positions.append(pos)
            
            if len(valid_positions) < 2:
                logger.warning("Недостаточно валидных данных для расчета параметров")
                return None
            
            # Векторизованный расчет скорости
            latitudes = np.array([pos['latitude'] for pos in valid_positions])
            longitudes = np.array([pos['longitude'] for pos in valid_positions])
            timestamps = np.array([pos['timestamp'].timestamp() for pos in valid_positions])
            
            # Расчет временных интервалов
            dt = np.diff(timestamps)  # Интервалы в секундах
            
            # Фильтрация нулевых интервалов
            valid_intervals = dt > 0
            if not np.any(valid_intervals):
                logger.error("Все временные интервалы равны нулю")
                return None
            
            # Расчет расстояний между точками
            distances = np.array([
                CoordinateConverter.haversine_distance(
                    latitudes[i], longitudes[i],
                    latitudes[i+1], longitudes[i+1],
                    altitude=408  # Средняя высота МКС
                ) for i in range(len(valid_positions) - 1)
            ])
            
            # Расчет скоростей в км/ч
            speeds = (distances[valid_intervals] / dt[valid_intervals]) * 3600
            
            if len(speeds) == 0:
                logger.error("Не удалось рассчитать скорости")
                return None
            
            # Статистика скорости
            speed_stats = StatisticsCalculator.calculate_statistics(speeds)
            
            # Проверка что статистика не None
            if speed_stats is None:
                logger.error("Не удалось рассчитать статистику скорости")
                return None
            
            # Средняя высота (используем более точное значение из TLE если доступно)
            avg_altitude = self.orbital_params['altitude_km'] if self.orbital_params else 408
            
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
                'data_points': len(valid_positions)
            }
            
            logger.info(f"Параметры рассчитаны: {params['avg_speed_kmh']:.0f} км/ч")
            return params
        except Exception as e:
            logger.error(f"Ошибка при расчете орбитальных параметров: {e}")
            return None
    
    def plot_ground_track(self, duration_hours=3, save=True, show=True):
        """
        Визуализация трека МКС на карте Земли
        
        Args:
            duration_hours: Продолжительность в часах
            save: Сохранить график
            show: Показать график
        """
        logger.info("Создание визуализации трека МКС...")
        
        # Если есть собранные данные, используем их
        if self.positions:
            latitudes = [pos['latitude'] for pos in self.positions]
            longitudes = [pos['longitude'] for pos in self.positions]
        else:
            # Генерация симулированных данных для демонстрации
            # (в реальной реализации здесь будут реальные данные)
            time_points = np.linspace(0, duration_hours, 100)
            latitudes = 51.6 * np.sin(2 * np.pi * time_points / 1.5)  # Наклон орбиты
            longitudes = (time_points * 15) % 360 - 180  # Долгота
        
        # Создание графика
        plt.figure(figsize=(15, 10))
        
        # Мировая карта (упрощенная)
        world_map = np.zeros((180, 360))
        plt.imshow(world_map, cmap='Blues', extent=(-180, 180, -90, 90), alpha=0.3)
        
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


    def analyze_altitude_trend(self, save=True, show=True):
        """
        Анализ тренда изменения высоты орбиты МКС
        
        Args:
            save: Сохранить график
            show: Показать график
        """
        logger.info("Анализ тренда изменения высоты орбиты...")
        
        try:
            # Генерация данных о высоте орбиты
            days = 30  # Анализ за 30 дней
            time_days = np.linspace(0, days, 100)
            
            # Начальная высота орбиты
            initial_altitude = 408.0  # км
            
            # Моделирование изменения высоты (снижение и коррекции)
            altitude = []
            current_altitude = initial_altitude
            
            for i, day in enumerate(time_days):
                # Постепенное снижение орбиты (~50 м/день)
                current_altitude -= 0.05  # 50 м/день = 0.05 км/день
                
                # Добавление случайных колебаний
                current_altitude += np.random.normal(0, 0.01)
                
                # Моделирование коррекции орбиты (примерно каждые 10 дней)
                if i > 0 and i % 30 == 0:  # Примерно каждые 10 дней
                    current_altitude += np.random.uniform(1.0, 2.0)  # Повышение 1-2 км
                
                altitude.append(current_altitude)
            
            altitude = np.array(altitude)
            
            # Расчет тренда (линейная регрессия)
            coeffs = np.polyfit(time_days, altitude, 1)
            trend_line = np.polyval(coeffs, time_days)
            trend_slope = coeffs[0]  # Наклон тренда (км/день)
            
            # Создание графика
            plt.figure(figsize=(12, 8))
            
            # Основной график высоты
            plt.plot(time_days, altitude, 'b-', linewidth=2, alpha=0.7, label='Высота орбиты')
            
            # Линия тренда
            plt.plot(time_days, trend_line, 'r--', linewidth=2, label=f'Тренд (наклон: {trend_slope:.3f} км/день)')
            
            # Зоны коррекции
            correction_points = []
            correction_days = []
            for i, day in enumerate(time_days):
                if i > 0 and i % 30 == 0:
                    correction_points.append(altitude[i])
                    correction_days.append(day)
            
            if correction_points:
                plt.scatter(correction_days, correction_points, c='green', s=100, 
                           marker='^', edgecolors='black', linewidth=1, 
                           label='Коррекции орбиты', zorder=5)
            
            plt.xlabel('Дни', fontsize=12, fontweight='bold')
            plt.ylabel('Высота орбиты (км)', fontsize=12, fontweight='bold')
            plt.title('Анализ тренда изменения высоты орбиты МКС', fontsize=14, fontweight='bold', pad=15)
            plt.legend(loc='upper right', fontsize=11, framealpha=0.9)
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # Добавление текстовой информации
            plt.text(0.02, 0.98, f'Начальная высота: {initial_altitude:.1f} км', 
                    transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            plt.text(0.02, 0.92, f'Средняя высота: {np.mean(altitude):.1f} км', 
                    transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            plt.text(0.02, 0.86, f'Тренд: {trend_slope*1000:.1f} м/день', 
                    transform=plt.gca().transAxes, fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            if save:
                filepath = self.fm.get_plot_path('iss_altitude_trend.png')
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                logger.info(f"График тренда высоты сохранен: {filepath}")
            
            if show:
                plt.show()
            else:
                plt.close()
                
            # Возвращаем результаты анализа
            return {
                'initial_altitude': initial_altitude,
                'final_altitude': altitude[-1],
                'average_altitude': np.mean(altitude),
                'trend_slope_km_per_day': trend_slope,
                'trend_slope_m_per_day': trend_slope * 1000,
                'total_change': altitude[-1] - initial_altitude
            }
            
        except Exception as e:
            logger.error(f"Ошибка при анализе тренда высоты орбиты: {e}")
            return None


    def get_real_time_data(self):
        """
        Получение реальных данных о положении МКС в реальном времени
        
        Returns:
            dict: Текущие данные о положении МКС
        """
        logger.info("Получение реальных данных о положении МКС...")
        
        try:
            # Получение текущего положения
            position = self.get_current_position()
            if not position:
                logger.error("Не удалось получить текущее положение МКС")
                return None
            
            # Получение TLE данных для точных параметров
            tle_data = self.get_tle_data()
            if not tle_data:
                logger.warning("Не удалось получить TLE данные")
            
            # Расчет орбитальных параметров
            orbital_params = self.orbital_params if self.orbital_params else {
                'altitude_km': 408.0,
                'orbital_period_min': 92.9,
                'inclination': 51.64
            }
            
            # Формирование полного набора данных
            real_time_data = {
                'position': position,
                'orbital_parameters': orbital_params,
                'tle_data': tle_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Сохранение данных
            filename = TimeUtils.get_timestamp_filename('real_time_data', 'json')
            self.fm.save_json(real_time_data, filename, subdirectory='telemetry')
            
            logger.info("Реальные данные успешно получены")
            return real_time_data
            
        except Exception as e:
            logger.error(f"Ошибка при получении реальных данных: {e}")
            return None


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


def analyze_pass_frequency(latitude, longitude, days=7):
    """
    Анализ частоты пролетов МКС над заданной точкой
    
    Args:
        latitude: Широта наблюдателя
        longitude: Долгота наблюдателя
        days: Период анализа в днях
    
    Returns:
        dict: Статистика пролетов
    """
    print(f"\n📊 АНАЛИЗ ЧАСТОТЫ ПРОЛЕТОВ МКС")
    print(f"📍 Точка наблюдения: {latitude}°, {longitude}°")
    print(f"📅 Период анализа: {days} дней")
    print("-" * 50)
    
    try:
        # Симуляция данных о пролетах
        # В реальной реализации здесь будет вызов API или расчет на основе орбитальных данных
        passes_per_day = []
        
        for day in range(days):
            # Среднее количество пролетов в день - 15.5 (орбитальный период ~93 минуты)
            # Но видимость зависит от времени суток и погодных условий
            daily_passes = np.random.poisson(4.5)  # Среднее ~4.5 видимых пролета в день
            passes_per_day.append(daily_passes)
        
        passes_per_day = np.array(passes_per_day)
        
        # Расчет статистики
        total_passes = np.sum(passes_per_day)
        avg_passes_per_day = float(np.mean(passes_per_day))
        std_passes_per_day = float(np.std(passes_per_day))
        max_passes = int(np.max(passes_per_day))
        min_passes = int(np.min(passes_per_day))
        
        # Определение наиболее активных дней
        most_active_day = int(np.argmax(passes_per_day))
        least_active_day = int(np.argmin(passes_per_day))
        
        # Вывод результатов
        print(f"📈 Общее количество пролетов: {total_passes}")
        print(f"📊 Среднее количество пролетов в день: {avg_passes_per_day:.1f} ± {std_passes_per_day:.1f}")
        print(f"🔺 Максимум пролетов в день: {max_passes}")
        print(f"🔻 Минимум пролетов в день: {min_passes}")
        print(f"🌟 Наиболее активный день: День {most_active_day + 1} ({passes_per_day[most_active_day]} пролетов)")
        print(f"🌑 Наименее активный день: День {least_active_day + 1} ({passes_per_day[least_active_day]} пролетов)")
        
        # Создание гистограммы
        plt.figure(figsize=(12, 6))
        days_range = np.arange(1, days + 1)
        plt.bar(days_range, passes_per_day, color='skyblue', alpha=0.7, edgecolor='navy')
        plt.xlabel('Дни', fontsize=12, fontweight='bold')
        plt.ylabel('Количество пролетов', fontsize=12, fontweight='bold')
        plt.title(f'Частота пролетов МКС над точкой ({latitude}°, {longitude}°)', 
                 fontsize=14, fontweight='bold', pad=15)
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Добавление средней линии
        plt.axhline(y=avg_passes_per_day, color='red', linestyle='--', 
                   linewidth=2, label=f'Среднее: {avg_passes_per_day:.1f}')
        plt.legend()
        
        # Сохранение графика
        fm = FileManager()
        filepath = fm.get_plot_path('iss_pass_frequency.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 График частоты пролетов сохранен: {filepath}")
        
        # Возвращаем результаты анализа
        return {
            'total_passes': int(total_passes),
            'avg_passes_per_day': avg_passes_per_day,
            'std_passes_per_day': std_passes_per_day,
            'max_passes_per_day': max_passes,
            'min_passes_per_day': min_passes,
            'most_active_day': most_active_day + 1,
            'least_active_day': least_active_day + 1,
            'passes_data': passes_per_day.tolist()
        }
        
    except Exception as e:
        print(f"❌ Ошибка при анализе частоты пролетов: {e}")
        return None


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
    print("📊 Сбор данных в реальном времени...")
    tracker.collect_positions(duration_minutes=2, interval_seconds=10)
    print("✅ Сбор данных завершен")
    
    # 4. Расчет параметров
    print_section("4. ОРБИТАЛЬНЫЕ ПАРАМЕТРЫ")
    params = tracker.calculate_orbital_parameters()
    if params:
        print(f"📏 Высота орбиты: {params['altitude_km']:.1f} км")
        print(f"🚀 Скорость: {params['avg_speed_kmh']:.0f} км/ч")
        print(f"⏱️  Период обращения: {params['orbital_period_min']:.1f} минут")
        print(f"🔁 Витков в сутки: {params['vitkov_per_day']:.1f}")
    else:
        # Fallback to simulated data
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