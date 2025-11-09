"""
ISS Environment Analysis Module
Модуль для анализа условий окружающей среды на МКС
(температура, радиация, атмосферное торможение)
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
from pathlib import Path

# Импорт утилит
try:
    from utils import (
        FileManager, OrbitalCalculations, TimeUtils,
        StatisticsCalculator, Logger, print_header, print_section
    )
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import (
        FileManager, OrbitalCalculations, TimeUtils,
        StatisticsCalculator, Logger, print_header, print_section
    )

# Константы окружающей среды
INTERNAL_TEMP_MIN = 18  # °C - минимальная внутренняя температура
INTERNAL_TEMP_MAX = 27  # °C - максимальная внутренняя температура
EXTERNAL_TEMP_SUN = 121  # °C - температура на солнце
EXTERNAL_TEMP_SHADOW = -157  # °C - температура в тени
ORBITAL_PERIOD = 92.9  # минуты - период обращения МКС
RADIATION_BASE = 30  # мкЗв/час - базовый уровень радиации
ISS_ALTITUDE = 408  # км - средняя высота МКС
TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"



# Настройка логирования
logger = Logger.setup_logger('iss_environment_analysis')


def parse_tle_data(tle_line1, tle_line2):
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


class ISSEnvironmentAnalyzer:
    """
    Класс для анализа условий окружающей среды на МКС
    Моделирует температуру, радиацию и высоту орбиты
    """
    
    def __init__(self, file_manager=None):
        """
        Инициализация анализатора
        
        Args:
            file_manager: Менеджер файлов (опционально)
        """
        self.fm = file_manager if file_manager else FileManager()
        self.tle_data = None
        self.orbital_params = None
        
        logger.info("ISSEnvironmentAnalyzer инициализирован")
    
    def get_tle_data(self):
        """
        Получение TLE (Two-Line Element) данных МКС
        TLE содержит точные орбитальные параметры
        
        Returns:
            dict: TLE данные или None при ошибке
        """
        logger.info("Получение TLE данных...")
        
        try:
            response = requests.get(TLE_URL, timeout=15)
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
                
                # Парсинг орбитальных параметров
                self.orbital_params = parse_tle_data(tle_data['line1'], tle_data['line2'])
                
                # Обновление константы высоты орбиты
                global ISS_ALTITUDE
                ISS_ALTITUDE = self.orbital_params['altitude_km']
                
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
    
    def simulate_temperature_profile(self, n_points=200, duration_hours=24):
        """
        Симуляция температурных условий МКС
        
        Температура зависит от:
        - Освещенности солнцем (дневная/ночная сторона орбиты)
        - Работы систем термоконтроля
        - Внешней температуры космоса
        
        Args:
            n_points: Количество точек данных
            duration_hours: Продолжительность симуляции в часах
        
        Returns:
            tuple: (time_hours, internal_temp, external_temp)
        """
        logger.info(f"Симуляция температурного профиля: {duration_hours}ч, {n_points} точек")
        
        time_hours = np.linspace(0, duration_hours, n_points)
        
        # Используем точный период обращения из TLE, если доступен
        orbital_period = self.orbital_params['orbital_period_min'] if self.orbital_params else ORBITAL_PERIOD
        orbital_period_hours = orbital_period / 60
        
        # Внутренняя температура (стабилизирована системами)
        # Небольшие колебания из-за активности экипажа и оборудования
        internal_temp = 22 + 2 * np.sin(2 * np.pi * time_hours / 12)
        internal_temp += np.random.normal(0, 0.5, n_points)  # Случайные флуктуации
        internal_temp = np.clip(internal_temp, INTERNAL_TEMP_MIN, INTERNAL_TEMP_MAX)
        
        # Внешняя температура (солнечная/теневая сторона)
        # МКС делает ~16 витков в сутки, ~1.5 часа на виток
        external_temp = []
        
        for t in time_hours:
            # Фаза орбиты (0-1)
            phase = (t % orbital_period_hours) / orbital_period_hours
            
            if phase < 0.6:  # Освещенная сторона (60% орбиты)
                # Постепенный нагрев на солнце
                temp = 40 + (EXTERNAL_TEMP_SUN - 40) * np.sin(np.pi * phase / 0.6)
            else:  # Теневая сторона (40% орбиты)
                # Быстрое охлаждение в тени
                temp = EXTERNAL_TEMP_SHADOW + (40 - EXTERNAL_TEMP_SHADOW) * np.sin(np.pi * (phase - 0.6) / 0.4)
            
            # Добавление случайных вариаций
            temp += np.random.normal(0, 5)
            external_temp.append(temp)
        
        external_temp = np.array(external_temp)
        
        logger.info("Температурный профиль создан")
        return time_hours, internal_temp, external_temp
    
    def simulate_radiation_levels(self, n_points=200, duration_hours=24):
        """
        Симуляция уровней радиации на МКС
        
        Источники радиации:
        - Галактические космические лучи (ГКЛ) - постоянный фон
        - Солнечные вспышки - редкие пики
        - Радиационные пояса Земли (особенно SAA - South Atlantic Anomaly)
        
        Args:
            n_points: Количество точек данных
            duration_hours: Продолжительность симуляции в часах
        
        Returns:
            tuple: (time_hours, radiation_levels)
        """
        logger.info(f"Симуляция радиационного профиля: {duration_hours}ч")
        
        time_hours = np.linspace(0, duration_hours, n_points)
        radiation = []
        
        # Используем точный период обращения из TLE, если доступен
        orbital_period = self.orbital_params['orbital_period_min'] if self.orbital_params else ORBITAL_PERIOD
        orbital_period_hours = orbital_period / 60
        
        for t in time_hours:
            # Базовый уровень ГКЛ с флуктуациями
            level = RADIATION_BASE * (1 + 0.2 * np.random.randn())
            
            # Пролет через Южно-Атлантическую аномалию (SAA)
            # SAA встречается примерно 2-3 раза в сутки на орбите с наклонением 51.6°
            orbit_number = t / orbital_period_hours
            
            # Проверка пролета через SAA
            if (orbit_number % 7 < 0.3) or (orbit_number % 13 < 0.3):
                # Резкое повышение радиации в SAA
                saa_multiplier = 2 + 2 * np.random.rand()
                level *= saa_multiplier
            
            # Редкие солнечные вспышки (2% вероятность на каждую точку)
            if np.random.rand() < 0.02:
                solar_flare_multiplier = 5 + 5 * np.random.rand()
                level *= solar_flare_multiplier
                logger.debug(f"Солнечная вспышка в t={t:.1f}ч, уровень={level:.1f}")
            
            # Вариации от солнечной активности (11-летний цикл - упрощено)
            solar_cycle_factor = 1 + 0.3 * np.sin(2 * np.pi * t / (24 * 365 * 5.5))
            level *= solar_cycle_factor
            
            radiation.append(max(level, 0))
        
        radiation = np.array(radiation)
        
        logger.info(f"Радиационный профиль создан. Средний уровень: {np.mean(radiation):.1f} мкЗв/ч")
        return time_hours, radiation
    
    def simulate_altitude_profile(self, n_points=200, duration_hours=24):
        """
        Симуляция изменения высоты орбиты МКС
        
        Включает:
        - Постепенное снижение из-за атмосферного торможения
        - Коррекции орбиты двигателями
        
        Args:
            n_points: Количество точек
            duration_hours: Продолжительность в часах
        
        Returns:
            tuple: (time_hours, altitude)
        """
        logger.info(f"Симуляция профиля высоты: {duration_hours}ч")
        
        time_hours = np.linspace(0, duration_hours, n_points)
        
        # Используем точную высоту из TLE, если доступна
        initial_altitude = self.orbital_params['altitude_km'] if self.orbital_params else ISS_ALTITUDE
        
        # Скорость снижения: ~50-100 м в сутки = ~2-4 м/час
        decay_rate = 0.003  # км/час (3 м/час)
        
        altitude = []
        current_altitude = initial_altitude
        
        for i, t in enumerate(time_hours):
            # Атмосферное торможение
            current_altitude -= decay_rate
            
            # Добавление шума (микроколебания)
            noise = np.random.normal(0, 0.01)
            current_altitude += noise
            
            # Симуляция коррекции орбиты
            # Обычно происходит раз в 1-2 месяца, но для демонстрации сделаем чаще
            if duration_hours > 18 and 18 <= t <= 19:
                # Коррекция: повышение на 1-2 км
                boost = 0.005 * (t - 18) * 200  # Постепенное повышение
                current_altitude += boost
            
            altitude.append(current_altitude)
        
        altitude = np.array(altitude)
        
        logger.info(f"Профиль высоты создан. Диапазон: {altitude.min():.2f}-{altitude.max():.2f} км")
        return time_hours, altitude
    
    def plot_environmental_conditions(self, duration_hours=24, save=True, show=True):
        """
        Визуализация всех условий окружающей среды на одном изображении
        
        Args:
            duration_hours: Продолжительность симуляции
            save: Сохранить график
            show: Показать график
        """
        logger.info("Создание комплексного графика условий среды...")
        
        # Генерация данных
        time_t, internal_temp, external_temp = self.simulate_temperature_profile(200, duration_hours)
        time_r, radiation = self.simulate_radiation_levels(200, duration_hours)
        time_a, altitude = self.simulate_altitude_profile(200, duration_hours)
        
        # Создание графиков
        fig, axes = plt.subplots(3, 1, figsize=(16, 14))
        
        # График 1: Температура
        ax1 = axes[0]
        ax1.plot(time_t, internal_temp, 'b-', linewidth=2.5, label='Внутри модулей', alpha=0.9)
        ax1.plot(time_t, external_temp, 'r-', linewidth=2.5, label='Внешняя оболочка', alpha=0.9)
        ax1.axhline(y=22, color='g', linestyle='--', alpha=0.4, linewidth=2, label='Целевая температура')
        ax1.fill_between(time_t, INTERNAL_TEMP_MIN, INTERNAL_TEMP_MAX, 
                         alpha=0.15, color='green', label='Комфортный диапазон')
        ax1.set_xlabel('Время (часы)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Температура (°C)', fontsize=12, fontweight='bold')
        ax1.set_title('Температурный профиль МКС', fontsize=14, fontweight='bold', pad=15)
        ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xlim(0, duration_hours)
        
        # График 2: Радиация
        ax2 = axes[1]
        ax2.plot(time_r, radiation, 'purple', linewidth=2, alpha=0.8)
        ax2.fill_between(time_r, 0, radiation, alpha=0.25, color='purple')
        ax2.axhline(y=RADIATION_BASE, color='orange', linestyle='--', 
                   linewidth=2, alpha=0.7, label=f'Средний уровень ({RADIATION_BASE} мкЗв/ч)')
        ax2.axhline(y=100, color='red', linestyle='--', linewidth=2, 
                   alpha=0.7, label='Повышенный уровень (100 мкЗв/ч)')
        
        # Отметка пиков SAA
        saa_times = []
        saa_radiation_values = []
        for i, level in enumerate(radiation):
            if level > RADIATION_BASE * 2:
                saa_times.append(time_r[i])
                # Make sure we don't go out of bounds
                idx = min(int(i), len(radiation) - 1)
                saa_radiation_values.append(radiation[idx])
        
        if saa_times and saa_radiation_values:
            ax2.scatter(saa_times, saa_radiation_values, 
                       c='red', s=50, alpha=0.6, zorder=5, label='Пики SAA/вспышки')
        
        ax2.set_xlabel('Время (часы)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Доза радиации (мкЗв/час)', fontsize=12, fontweight='bold')
        ax2.set_title('Уровень космической радиации на МКС', fontsize=14, fontweight='bold', pad=15)
        ax2.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xlim(0, duration_hours)
        
        # График 3: Высота орбиты
        ax3 = axes[2]
        ax3.plot(time_a, altitude, 'green', linewidth=2.5, alpha=0.9)
        ax3.axhline(y=ISS_ALTITUDE, color='blue', linestyle='--', 
                   linewidth=2, alpha=0.5, label=f'Номинальная высота ({ISS_ALTITUDE} км)')
        ax3.fill_between(time_a, 400, 420, alpha=0.15, color='blue', label='Рабочий диапазон')
        
        # Отметка коррекции
        if duration_hours > 18:
            ax3.axvspan(18, 19, alpha=0.2, color='orange', label='Коррекция орбиты')
            ax3.annotate('Коррекция двигателями', xy=(18.5, altitude.max() - 0.5),
                        xytext=(15, altitude.max() - 2),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2),
                        fontsize=11, fontweight='bold', color='red')
        
        ax3.set_xlabel('Время (часы)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Высота орбиты (км)', fontsize=12, fontweight='bold')
        ax3.set_title('Высота орбиты МКС (с учетом атмосферного торможения)', 
                     fontsize=14, fontweight='bold', pad=15)
        ax3.legend(loc='lower left', fontsize=11, framealpha=0.9)
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.set_xlim(0, duration_hours)
        
        plt.tight_layout()
        
        if save:
            filepath = self.fm.get_plot_path('iss_environmental_conditions.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"График условий среды сохранен: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def analyze_radiation_exposure(self, days=30, save=True, show=True):
        """
        Анализ накопленной дозы радиации за период
        
        Args:
            days: Количество дней для анализа
            save: Сохранить график
            show: Показать график
        
        Returns:
            float: Общая накопленная доза в мЗв
        """
        logger.info(f"Анализ радиационного воздействия за {days} дней...")
        
        hours = days * 24
        time_h, radiation = self.simulate_radiation_levels(hours * 4, hours)
        
        # Накопленная доза (интегрирование)
        cumulative_dose = np.cumsum(radiation) * (hours / len(radiation))  # мкЗв
        total_dose_mSv = cumulative_dose[-1] / 1000  # мЗв
        
        # Статистика
        radiation_stats = StatisticsCalculator.calculate_statistics(radiation)
        
        # Нормы и лимиты
        annual_limit_public = 1  # мЗв/год
        annual_limit_workers = 20  # мЗв/год
        astronaut_career_limit = 1000  # мЗв за карьеру
        
        # Вывод результатов
        print(f"\n{'='*70}")
        print(f"📊 АНАЛИЗ РАДИАЦИОННОГО ВОЗДЕЙСТВИЯ ({days} дней)")
        print(f"{'='*70}\n")
        print(f"Накопленная доза: {total_dose_mSv:.2f} мЗв")
        print(f"Средняя доза в день: {total_dose_mSv/days:.2f} мЗв/день")
        
        # Проверка статистики
        if radiation_stats is not None:
            print(f"Средняя доза в час: {radiation_stats['mean']:.2f} мкЗв/ч")
            print(f"Максимальный пик: {radiation_stats['max']:.2f} мкЗв/ч")
            print(f"Стандартное отклонение: {radiation_stats['std']:.2f} мкЗв/ч")
        else:
            print("Статистика недоступна")
            
        print(f"\nЭкстраполяция на год: {total_dose_mSv * 365/days:.1f} мЗв/год")
        print(f"\n📋 Сравнение с нормами:")
        print(f"  • Годовой лимит (население): {annual_limit_public} мЗв/год")
        print(f"  • Годовой лимит (работники): {annual_limit_workers} мЗв/год")
        print(f"  • Карьерный лимит (астронавты): {astronaut_career_limit} мЗв")
        print(f"\n⚠️  Превышение годового лимита населения: {(total_dose_mSv * 365/days) / annual_limit_public:.1f}x")
        print(f"\n{'='*70}\n")
        
        # Визуализация
        plt.figure(figsize=(14, 7))
        
        time_days = time_h / 24
        cumulative_dose_mSv = cumulative_dose / 1000
        
        plt.plot(time_days, cumulative_dose_mSv, 'purple', linewidth=2.5, alpha=0.9)
        plt.fill_between(time_days, 0, cumulative_dose_mSv, alpha=0.2, color='purple')
        
        # Референсные линии
        plt.axhline(y=annual_limit_public * (days/365), color='green', 
                   linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Лимит для населения ({annual_limit_public * (days/365):.2f} мЗв за {days} дней)')
        plt.axhline(y=annual_limit_workers * (days/365), color='orange', 
                   linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Лимит для работников ({annual_limit_workers * (days/365):.2f} мЗв за {days} дней)')
        
        plt.xlabel('Время (дни)', fontsize=13, fontweight='bold')
        plt.ylabel('Накопленная доза (мЗв)', fontsize=13, fontweight='bold')
        plt.title(f'Накопленная радиационная доза на МКС за {days} дней', 
                 fontsize=15, fontweight='bold', pad=15)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(loc='upper left', fontsize=11, framealpha=0.9)
        plt.tight_layout()
        
        if save:
            filepath = self.fm.get_plot_path('iss_cumulative_radiation.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"График накопленной радиации сохранен: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        # Сохранение данных анализа
        analysis_data = {
            'duration_days': days,
            'total_dose_mSv': total_dose_mSv,
            'daily_dose_mSv': total_dose_mSv / days,
            'extrapolated_annual_mSv': total_dose_mSv * 365 / days,
            'radiation_stats': radiation_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        self.fm.save_json(analysis_data, 'radiation_analysis.json', subdirectory='analysis')
        
        logger.info(f"Анализ завершен. Общая доза: {total_dose_mSv:.2f} мЗв")
        return total_dose_mSv
    
    def generate_telemetry_report(self):
        """Генерация комплексного телеметрического отчета"""
        
        print_header("КОМПЛЕКСНЫЙ ТЕЛЕМЕТРИЧЕСКИЙ ОТЧЕТ МКС")
        
        # Используем точные параметры из TLE, если доступны
        if self.orbital_params:
            orbital_period = self.orbital_params['orbital_period_min']
            altitude = self.orbital_params['altitude_km']
            inclination = self.orbital_params['inclination']
        else:
            orbital_period = ORBITAL_PERIOD
            altitude = ISS_ALTITUDE
            inclination = 51.64
        
        # Орбитальные параметры
        print("\n📡 ОРБИТАЛЬНЫЕ ПАРАМЕТРЫ:")
        print(f"   • Средняя высота: {altitude:.1f} км")
        print(f"   • Наклонение орбиты: {inclination:.2f}°")
        print(f"   • Период обращения: ~{orbital_period:.1f} минут")
        print(f"   • Витков в сутки: ~{24 * 60 / orbital_period:.1f}")
        
        velocity = OrbitalCalculations.calculate_orbital_velocity(altitude)
        print(f"   • Орбитальная скорость: ~{velocity:.2f} км/с ({velocity*3600:.0f} км/ч)")
        
        # Температурные условия
        print("\n🌡️  ТЕМПЕРАТУРНЫЕ УСЛОВИЯ:")
        print(f"   • Внутри модулей: {INTERNAL_TEMP_MIN}-{INTERNAL_TEMP_MAX}°C")
        print(f"   • Целевая температура: 22°C")
        print(f"   • Внешняя оболочка (солнце): до +{EXTERNAL_TEMP_SUN}°C")
        print(f"   • Внешняя оболочка (тень): до {EXTERNAL_TEMP_SHADOW}°C")
        print(f"   • Циклов нагрев/охлаждение: ~{24 * 60 / orbital_period:.0f} в сутки")
        print(f"   • Перепад температур: {EXTERNAL_TEMP_SUN - EXTERNAL_TEMP_SHADOW}°C")
        
        # Радиационная обстановка
        print("\n☢️  РАДИАЦИОННАЯ ОБСТАНОВКА:")
        print(f"   • Средний уровень: {RADIATION_BASE} мкЗв/час")
        print(f"   • Доза в сутки: ~{RADIATION_BASE * 24 / 1000:.2f} мЗв")
        print(f"   • Годовая доза: ~{RADIATION_BASE * 24 * 365 / 1000:.0f} мЗв")
        print(f"   • Пики в SAA: до 3-5x выше фона")
        print(f"   • Солнечные вспышки: до 10x выше фона (редко)")
        print(f"   • Сравнение с Землей: в ~150-300 раз выше")
        
        # Атмосферное торможение
        print("\n🛰️  АТМОСФЕРНОЕ ТОРМОЖЕНИЕ:")
        drag_coef = OrbitalCalculations.atmospheric_drag_coefficient(altitude)
        print(f"   • Снижение орбиты: ~50-100 м/сутки")
        print(f"   • Коэффициент торможения: {drag_coef:.1f} (относительный)")
        print(f"   • Коррекции орбиты: ~2-4 раза в год")
        print(f"   • Повышение за коррекцию: ~1-2 км")
        print(f"   • Расход топлива: ~7-8 тонн/год")
        
        # Системы жизнеобеспечения
        print("\n🔧 СИСТЕМЫ ЖИЗНЕОБЕСПЕЧЕНИЯ:")
        print(f"   • Регенерация воздуха: CO₂ → O₂")
        print(f"   • Регенерация воды: ~93% эффективность")
        print(f"   • Термоконтроль: радиаторы и теплообменники")
        print(f"   • Защита от радиации: экранирование модулей")
        print(f"   • Защита от микрометеоритов: многослойная обшивка")
        
        print(f"\n{'='*70}\n")
        
        logger.info("Отчет сгенерирован")
        
        # Сохранение отчета в файл
        report_data = {
            'report_date': datetime.now().isoformat(),
            'orbital_parameters': {
                'altitude_km': altitude,
                'inclination_deg': inclination,
                'period_min': orbital_period,
                'velocity_kms': velocity
            },
            'temperature': {
                'internal_min': INTERNAL_TEMP_MIN,
                'internal_max': INTERNAL_TEMP_MAX,
                'external_sun': EXTERNAL_TEMP_SUN,
                'external_shadow': EXTERNAL_TEMP_SHADOW
            },
            'radiation': {
                'base_level_uSv_h': RADIATION_BASE,
                'daily_dose_mSv': RADIATION_BASE * 24 / 1000,
                'annual_dose_mSv': RADIATION_BASE * 24 * 365 / 1000
            }
        }
        
        filename = TimeUtils.get_timestamp_filename('telemetry_report', 'json')
        self.fm.save_json(report_data, filename, subdirectory='reports')


def main():
    """Основная функция для запуска анализа окружающей среды"""
    
    print_header("АНАЛИЗ УСЛОВИЙ ОКРУЖАЮЩЕЙ СРЕДЫ МКС")
    
    analyzer = ISSEnvironmentAnalyzer()
    
    # 1. Получение TLE данных
    print_section("1. ПОЛУЧЕНИЕ TLE ДАННЫХ")
    tle_data = analyzer.get_tle_data()
    if tle_data:
        print(f"   ✓ Спутник: {tle_data['name']}")
        print(f"   ✓ TLE Line 1: {tle_data['line1'][:40]}...")
        print(f"   ✓ TLE Line 2: {tle_data['line2'][:40]}...")
        print(f"   ✓ Время получения: {tle_data['timestamp']}")
    else:
        print("   ⚠️  Не удалось получить TLE данные")
    
    # 2. Анализ условий окружающей среды
    print_section("2. АНАЛИЗ УСЛОВИЙ ОКРУЖАЮЩЕЙ СРЕДЫ")
    print("   📊 Создание графиков температуры, радиации и высоты...")
    analyzer.plot_environmental_conditions(duration_hours=24, show=False)
    print("   ✓ Графики созданы и сохранены")
    
    # 3. Анализ радиационного воздействия
    print_section("3. АНАЛИЗ РАДИАЦИОННОГО ВОЗДЕЙСТВИЯ")
    total_dose = analyzer.analyze_radiation_exposure(days=180, show=False)
    print(f"   ✓ Анализ завершен. Доза за 180 дней: {total_dose:.2f} мЗв")
    
    # 4. Генерация отчета
    print_section("4. КОМПЛЕКСНЫЙ ТЕЛЕМЕТРИЧЕСКИЙ ОТЧЕТ")
    analyzer.generate_telemetry_report()
    
    print_header("✓ АНАЛИЗ УСЛОВИЙ СРЕДЫ ЗАВЕРШЕН!")


if __name__ == "__main__":
    main()
