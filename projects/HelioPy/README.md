# 🌞 HelioPy

**Open-source библиотека для анализа солнечной активности и прогнозирования космической погоды на Python**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/yourusername/heliopy/ci.yml?branch=main)](https://github.com/yourusername/heliopy/actions)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen)](https://yourusername.github.io/heliopy/)
[![DOI](https://img.shields.io/badge/DOI-10.xxxx/xxxxxx-blue)](https://doi.org/10.xxxx/xxxxxx)

HelioPy — это современная библиотека с открытым исходным кодом для обработки данных солнечных наблюдений, анализа солнечной активности и прогнозирования космической погоды. Библиотека предоставляет единый интерфейс для работы с данными от различных космических миссий и наземных обсерваторий, а также включает инструменты для научного анализа и визуализации.

## 🚀 Основные возможности

### 📊 Работа с данными
- **Поддержка множества источников данных**:
  - SDO (AIA, HMI)
  - SOHO (LASCO, EIT)
  - STEREO (SECCHI)
  - GOES (XRS)
  - ACE (SWEPAM, MAG)
  - DSCOVR
- **Автоматическая загрузка и кэширование** данных
- **Единый формат данных** для всех источников
- **Предобработка данных**: калибровка, нормализация, коррекция искажений

### 🔍 Анализ солнечной активности
- **Обнаружение солнечных вспышек** (Flare Detection)
  - Автоматическая классификация по классам (A, B, C, M, X)
  - Анализ временных характеристик и энергетического спектра
- **Отслеживание корональных выбросов массы (CME)**
  - Автоматическое определение параметров: скорость, ускорение, направление
  - 3D реконструкция траектории
- **Анализ солнечных пятен и активных областей**
  - Классификация по типам (McIntosh, Hale)
  - Прогнозирование вспышечной активности

### 🌍 Прогнозирование космической погоды
- **Прогноз геомагнитных бурь**
  - Расчет индексов Kp, Dst, AE
  - Прогнозирование времени прибытия CME
- **Оценка радиационной опасности**
  - Прогноз солнечных протонных событий
  - Расчет доз облучения для космических аппаратов
- **Воздействие на технологические системы**
  - Оценка рисков для спутников
  - Анализ влияния на энергосистемы и системы связи

### 🎨 Визуализация
- **Интерактивные солнечные карты**
- **Анимации солнечных событий**
- **Мультиволновые визуализации**
- **3D визуализация CME**
- **Графики временных рядов и спектрограммы

## 🛠 Требования к установке

### Системные требования
- Python 3.8 или новее
- 4+ ГБ оперативной памяти (рекомендуется для работы с большими данными)
- 10+ ГБ свободного места на диске (для кэширования данных)

### Зависимости
- NumPy
- SciPy
- Pandas
- Matplotlib
- Astropy
- SunPy
- scikit-image
- scikit-learn
- netCDF4
- h5py
- tqdm
- requests
- beautifulsoup4

## 📦 Быстрая установка

### Установка с PyPI (рекомендуется)
```bash
pip install heliopy
```

### Установка из исходного кода

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/heliopy.git
cd heliopy

# Установка в виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# или
venv\Scripts\activate    # Windows

# Установка зависимостей
pip install -r requirements.txt

# Установка библиотеки в режиме разработки
pip install -e .
```

## ⚡ Быстрый старт

Пример 1: Загрузка и визуализация данных SDO

```python
from heliopy import data_loader, visualization

# Загрузка данных SDO/AIA для определенной даты
date = "2023-10-15"
wavelength = 193  # Å

# Автоматическая загрузка данных
sdo_data = data_loader.load_sdo_aia(date, wavelength)

# Создание визуализации
fig = visualization.plot_solar_image(
    sdo_data,
    title=f"SDO/AIA {wavelength}Å - {date}",
    save_path="sdo_image.png"
)

print("Изображение сохранено в sdo_image.png")
```

Пример 2: Обнаружение солнечных вспышек

```python
from heliopy import flare_detector, space_weather

# Загрузка данных GOES
goes_data = data_loader.load_goes("2023-10-15")

# Обнаружение вспышек
flares = flare_detector.detect_flares(goes_data)

print(f"Обнаружено вспышек: {len(flares)}")
for flare in flares:
    print(f"  Класс: {flare.class_}, Время начала: {flare.start_time}, Пик: {flare.peak_time}")

# Прогноз воздействия на Землю
impact_forecast = space_weather.forecast_geoeffectiveness(flares[-1])
print(f"\nПрогноз воздействия: {impact_forecast.summary}")
```

Пример 3: Отслеживание CME

```python
from heliopy import cme_detector, visualization

# Загрузка данных SOHO/LASCO
lasco_data = data_loader.load_soho_lasco("2023-10-15", "C2")

# Обнаружение и отслеживание CME
cme_events = cme_detector.track_cme(lasco_data)

# Визуализация траектории CME
visualization.plot_cme_trajectory(
    cme_events[0],
    save_path="cme_trajectory.png"
)

print(f"Скорость CME: {cme_events[0].speed:.1f} км/с")
print(f"Направление: {cme_events[0].direction} градусов")
```

## 📂 Подробная структура проекта HelioPy

```
HelioPy/
├── heliopy/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_loader.py          # Загрузка данных из различных источников
│   │   ├── data_processor.py       # Предобработка и очистка данных
│   │   ├── coordinate_systems.py   # Системы координат (гелиоцентрические и др.)
│   │   └── units.py                # Специализированные единицы измерения
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── flare_detector.py       # Обнаружение солнечных вспышек
│   │   ├── cme_detector.py         # Обнаружение корональных выбросов массы
│   │   ├── event_catalog.py        # Работа с каталогами событий
│   │   └── event_analyzer.py       # Анализ характеристик событий
│   │
│   ├── imaging/
│   │   ├── __init__.py
│   │   ├── image_processor.py      # Обработка солнечных изображений
│   │   ├── feature_extractor.py    # Извлечение признаков с изображений
│   │   ├── visualization.py        # Визуализация солнечных изображений
│   │   └── multi_wavelength.py     # Работа с мультиволновыми данными
│   │
│   ├── magnetic_fields/
│   │   ├── __init__.py
│   │   ├── field_reconstruction.py # Реконструкция магнитных полей
│   │   ├── field_extrapolation.py  # Экстраполяция полей в корону
│   │   ├── topology_analyzer.py    # Анализ топологии полей
│   │   └── reconnection_detector.py # Обнаружение магнитной реконнекции
│   │
│   ├── space_weather/
│   │   ├── __init__.py
│   │   ├── forecast_models.py      # Модели прогнозирования космической погоды
│   │   ├── impact_assessment.py    # Оценка воздействия на Землю
│   │   ├── radiation_models.py     # Модели радиационных поясов
│   │   └── geomagnetic_storms.py   # Анализ геомагнитных бурь
│   │
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── sdo_loader.py            # Данные с SDO (Solar Dynamics Observatory)
│   │   ├── soho_loader.py           # Данные с SOHO
│   │   ├── stereo_loader.py         # Данные с STEREO
│   │   ├── goes_loader.py           # Данные с GOES (вспышки)
│   │   ├── ace_loader.py            # Данные с ACE (солнечный ветер)
│   │   └── omni_loader.py           # Данные из OMNI базы
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mhd_simulator.py         # МГД симуляции
│   │   ├── particle_transport.py   # Транспорт частиц
│   │   ├── radiation_belt.py       # Модели радиационных поясов
│   │   └── ionosphere_coupling.py  # Связь с ионосферой
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── time_utils.py            # Работа со временем (UTC, UT1 и др.)
│   │   ├── math_utils.py            # Математические утилиты
│   │   ├── stats_utils.py           # Статистические методы
│   │   └── config.py                # Конфигурация библиотеки
│   │
│   └── visualization/
│       ├── __init__.py
│       ├── plotter.py              # Основные графики
│       ├── animation.py            # Анимации солнечных событий
│       ├── map_visualizer.py       # Визуализация карт
│       └── interactive.py          # Интерактивные визуализации
│
├── examples/
│   ├── basic_usage.ipynb           # Базовые примеры использования
│   ├── flare_analysis.ipynb        # Анализ солнечных вспышек
│   ├── cme_tracking.ipynb          # Отслеживание корональных выбросов
│   ├── space_weather_forecast.ipynb # Прогноз космической погоды
│   └── magnetic_field_modeling.ipynb # Моделирование магнитных полей
│
├── tests/
│   ├── unit/
│   │   ├── test_core.py
│   │   ├── test_events.py
│   │   ├── test_imaging.py
│   │   └── test_space_weather.py
│   ├── integration/
│   │   ├── test_data_pipeline.py
│   │   └── test_end_to_end.py
│   └── data/
│       └── sample_data/            # Примеры данных для тестов
│
├── docs/
│   ├── api_reference/
│   │   ├── core.rst
│   │   ├── events.rst
│   │   ├── imaging.rst
│   │   └── space_weather.rst
│   ├── tutorials/
│   │   ├── getting_started.rst
│   │   ├── data_analysis.rst
│   │   └── advanced_topics.rst
│   ├── user_guide.rst
│   ├── developer_guide.rst
│   └── conf.py                     # Конфигурация документации
│
├── data/
│   ├── sample_datasets/            # Примеры датасетов для быстрого старта
│   └── metadata/                   # Метаданные для различных источников
│
├── scripts/
│   ├── setup_environment.py        # Скрипт настройки окружения
│   ├── download_sample_data.py     # Скачивание примеров данных
│   └── validate_installation.py    # Проверка установки
│
├── configs/
│   ├── default_config.yaml         # Конфигурация по умолчанию
│   ├── data_sources.yaml           # Конфигурация источников данных
│   └── visualization.yaml          # Настройки визуализации
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # CI/CD пайплайн
│   │   ├── docs.yml               # Автоматическая сборка документации
│   │   └── release.yml            # Процесс релиза
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── requirements/
│   ├── base.txt                   # Основные зависимости
│   ├── dev.txt                    # Зависимости для разработки
│   ├── docs.txt                   # Зависимости для документации
│   └── test.txt                   # Зависимости для тестирования
│
├── setup.py                       # Установочный скрипт
├── pyproject.toml                 # Современная конфигурация сборки
├── README.md                      # Основное описание проекта
├── LICENSE                        # Лицензия (рекомендую MIT или Apache 2.0)
├── CONTRIBUTING.md                # Руководство для контрибьюторов
├── CODE_OF_CONDUCT.md             # Кодекс поведения
└── .gitignore                     # Игнорируемые файлы
```

## 🧪 Тестирование

**Для запуска тестов используйте pytest:**

```bash
# Установка зависимостей для тестирования
pip install -r requirements/test.txt

# Запуск всех тестов
pytest

# Запуск тестов с покрытием кода
pytest --cov=heliopy --cov-report=html
```
