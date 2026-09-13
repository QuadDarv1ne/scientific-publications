# 📚 Справка по API ISS Telemetry Analyzer

## 📖 Обзор API

ISS Telemetry Analyzer предоставляет программный интерфейс для работы с телеметрическими данными МКС. API разделен на два основных модуля:

1. **ISSTracker** - для орбитального анализа
2. **ISSEnvironmentAnalyzer** - для анализа условий окружающей среды

## 🛰️ Модуль ISSTracker

### Импорт
```python
from src.iss_orbital_analysis import ISSTracker
```

### Инициализация
```python
tracker = ISSTracker(file_manager=None)
```

### Методы

#### get_current_position()
Получение текущего положения МКС через Open Notify API.

**Возвращает:** `dict` или `None`
```python
{
    "latitude": float,  # Широта в градусах
    "longitude": float,  # Долгота в градусах
    "timestamp": datetime,  # Время измерения
}
```

#### get_tle_data()
Получение TLE данных МКС через CelesTrak API.

**Возвращает:** `dict` или `None`
```python
{
    "name": str,  # Название объекта
    "line1": str,  # Первая строка TLE
    "line2": str,  # Вторая строка TLE
    "timestamp": str,  # Время получения данных
}
```

#### collect_positions(duration_minutes=10, interval_seconds=30)
Сбор положений МКС за определенный период.

**Параметры:**
- `duration_minutes` (int) - длительность сбора в минутах
- `interval_seconds` (int) - интервал между измерениями в секундах

#### calculate_orbital_parameters()
Расчет орбитальных параметров на основе собранных данных.

**Возвращает:** `dict` или `None`
```python
{
    "altitude_km": float,  # Высота орбиты в км
    "avg_speed_kmh": float,  # Средняя скорость в км/ч
    "max_speed_kmh": float,  # Максимальная скорость в км/ч
    "min_speed_kmh": float,  # Минимальная скорость в км/ч
    "speed_std": float,  # Стандартное отклонение скорости
    "orbital_period_min": float,  # Период обращения в минутах
    "vitkov_per_day": float,  # Количество витков в сутки
    "data_points": int,  # Количество точек данных
}
```

#### plot_ground_track(duration_hours=3, save=True, show=True)
Визуализация трека МКС на карте Земли.

**Параметры:**
- `duration_hours` (int) - продолжительность в часах
- `save` (bool) - сохранить график
- `show` (bool) - показать график

#### plot_3d_orbit(save=True, show=True)
3D визуализация орбиты МКС.

**Параметры:**
- `save` (bool) - сохранить график
- `show` (bool) - показать график

#### analyze_altitude_trend(save=True, show=True)
Анализ тренда изменения высоты орбиты.

**Возвращает:** `dict` или `None`
```python
{
    "initial_altitude": float,  # Начальная высота
    "final_altitude": float,  # Конечная высота
    "average_altitude": float,  # Средняя высота
    "trend_slope_km_per_day": float,  # Наклон тренда в км/день
    "trend_slope_m_per_day": float,  # Наклон тренда в м/день
    "total_change": float,  # Общее изменение высоты
}
```

### Автономные функции

#### predict_passes(latitude, longitude, n_passes=5)
Прогноз видимости МКС для заданной точки.

**Параметры:**
- `latitude` (float) - широта наблюдателя
- `longitude` (float) - долгота наблюдателя
- `n_passes` (int) - количество прогнозируемых пролетов

#### analyze_pass_frequency(latitude, longitude, days=7)
Анализ частоты пролетов МКС над заданной точкой.

**Параметры:**
- `latitude` (float) - широта наблюдателя
- `longitude` (float) - долгота наблюдателя
- `days` (int) - период анализа в днях

**Возвращает:** `dict` или `None`
```python
{
    "total_passes": int,  # Общее количество пролетов
    "avg_passes_per_day": float,  # Среднее количество пролетов в день
    "std_passes_per_day": float,  # Стандартное отклонение
    "max_passes_per_day": int,  # Максимум пролетов в день
    "min_passes_per_day": int,  # Минимум пролетов в день
    "most_active_day": int,  # Наиболее активный день
    "least_active_day": int,  # Наименее активный день
    "passes_data": list,  # Данные о пролетах
}
```

## 🌡️ Модуль ISSEnvironmentAnalyzer

### Импорт
```python
from src.iss_environment_analysis import ISSEnvironmentAnalyzer
```

### Инициализация
```python
analyzer = ISSEnvironmentAnalyzer(file_manager=None)
```

### Методы

#### get_tle_data()
Получение TLE данных МКС через CelesTrak API.

**Возвращает:** `dict` или `None`
```python
{
    "name": str,  # Название объекта
    "line1": str,  # Первая строка TLE
    "line2": str,  # Вторая строка TLE
    "timestamp": str,  # Время получения данных
}
```

#### simulate_temperature_profile(n_points=200, duration_hours=24)
Симуляция температурных условий МКС.

**Параметры:**
- `n_points` (int) - количество точек данных
- `duration_hours` (int) - продолжительность симуляции в часах

**Возвращает:** `tuple` (time_hours, internal_temp, external_temp)

#### simulate_radiation_levels(n_points=200, duration_hours=24)
Симуляция уровней радиации на МКС.

**Параметры:**
- `n_points` (int) - количество точек данных
- `duration_hours` (int) - продолжительность симуляции в часах

**Возвращает:** `tuple` (time_hours, radiation)

#### simulate_altitude_profile(n_points=200, duration_hours=24)
Симуляция изменения высоты орбиты МКС.

**Параметры:**
- `n_points` (int) - количество точек
- `duration_hours` (int) - продолжительность в часах

**Возвращает:** `tuple` (time_hours, altitude)

#### plot_environmental_conditions(duration_hours=24, save=True, show=True)
Визуализация всех условий окружающей среды на одном изображении.

**Параметры:**
- `duration_hours` (int) - продолжительность симуляции
- `save` (bool) - сохранить график
- `show` (bool) - показать график

#### analyze_radiation_exposure(days=30, save=True, show=True)
Анализ накопленной дозы радиации за период.

**Параметры:**
- `days` (int) - количество дней для анализа
- `save` (bool) - сохранить график
- `show` (bool) - показать график

**Возвращает:** `float` - общая накопленная доза в мЗв

#### analyze_radiation_peaks(days=30)
Анализ пиков радиационного фона и их характеристик.

**Параметры:**
- `days` (int) - период анализа в днях

**Возвращает:** `dict` или `None`
```python
{
    "total_peaks": int,  # Общее количество пиков
    "max_peak": float,  # Максимальный пик
    "avg_peak": float,  # Средняя интенсивность пиков
    "std_peak": float,  # Стандартное отклонение пиков
    "peak_frequency_per_day": float,  # Частота пиков в день
    "peak_duration_avg_hours": float,  # Средняя продолжительность пиков
    "peak_intensity_ratio": float,  # Отношение интенсивности пиков к среднему уровню
}
```

#### generate_telemetry_report()
Генерация комплексного телеметрического отчета.

## 🧰 Вспомогательные модули

### FileManager
Менеджер для работы с файлами и директориями проекта.

### CoordinateConverter
Конвертер координат между различными системами.

### OrbitalCalculations
Класс для орбитальных вычислений.

### DataValidator
Валидатор данных телеметрии.

### TimeUtils
Утилиты для работы со временем.

### StatisticsCalculator
Калькулятор статистических параметров.

### Logger
Расширенный логгер для проекта.

## 📊 Примеры использования

### Пример 1: Орбитальный анализ
```python
from src.iss_orbital_analysis import ISSTracker

tracker = ISSTracker()
position = tracker.get_current_position()
params = tracker.calculate_orbital_parameters()
tracker.plot_ground_track()
```

### Пример 2: Анализ условий среды
```python
from src.iss_environment_analysis import ISSEnvironmentAnalyzer

analyzer = ISSEnvironmentAnalyzer()
analyzer.plot_environmental_conditions()
total_dose = analyzer.analyze_radiation_exposure(days=30)
```

### Пример 3: Прогноз видимости
```python
from src.iss_orbital_analysis import predict_passes, analyze_pass_frequency

# Прогноз для Москвы
predict_passes(55.7558, 37.6173, n_passes=5)

# Анализ частоты пролетов
frequency_data = analyze_pass_frequency(55.7558, 37.6173, days=7)
```

---
*Документация API для ISS Telemetry Analyzer*