# 🌞 HelioPy

**Open-source библиотека для анализа солнечной активности и прогнозирования космической погоды на Python**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![CI](https://github.com/QuadDarv1ne/scientific-publications/actions/workflows/ci.yml/badge.svg)](https://github.com/QuadDarv1ne/scientific-publications/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/QuadDarv1ne/scientific-publications/branch/main/graph/badge.svg)](https://codecov.io/gh/QuadDarv1ne/scientific-publications)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/heliopy/badge/?version=latest)](https://heliopy.readthedocs.io/en/latest/?badge=latest)

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
  - Helioviewer (много источников данных)
  - Parker Solar Probe (SWEAP, FIELDS)
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

### Запуск из командной строки (CLI)

- Справка:
  - `python -m heliopy --help`
- Информация о пакете:
  - `python -m heliopy info`
- Пример анализа (время + вращение Кэррингтона + преобразование координат):
  - `python -m heliopy analyze --time "2023-10-15 12:00:00"`

### Веб-интерфейс

Запуск веб-сайта на Flask:

- Через CLI:
  - `python -m heliopy web --host 127.0.0.1 --port 5010`
- Через Makefile:
  - `make web`

После запуска откройте браузер:

- Главная: `http://127.0.0.1:5010/`
- Анализ: `http://127.0.0.1:5010/analysis`
- Визуализация: `http://127.0.0.1:5010/visualization`
- API/Документация: `http://127.0.0.1:5010/api-docs`
- О проекте: `http://127.0.0.1:5010/about`
- Health-check: `http://127.0.0.1:5010/ping`
- API info: `http://127.0.0.1:5010/api/info`

Доступные demo API:

- `GET /api/flare/classify?flux=1e-6` — классификация вспышки по потоку (A/B/C/M/X)
- `GET /api/time/carrington?time=2023-10-15 12:00:00` — номер вращения Кэррингтона
- `POST /api/coords/convert` — тело `{ "r": 1.0, "theta": 0.5, "phi": 0.2 }` возвращает `{x,y,z}`

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
    sdo_data, title=f"SDO/AIA {wavelength}Å - {date}", save_path="sdo_image.png"
)

print("Изображение сохранено в sdo_image.png")
```

Пример 2: Загрузка данных с Helioviewer

```python
from heliopy import load_helioviewer

# Получение списка доступных источников данных
sources = data_loader.get_helioviewer_sources()

# Загрузка изображения с Helioviewer для определенной даты
# SDO/AIA 193Å (source_id = 14)
date = "2023-10-15T12:00:00"
helio_data = load_helioviewer(date, source_id=14)

# Создание визуализации
fig = visualization.plot_solar_image(
    helio_data, title=f"Helioviewer SDO/AIA 193Å - {date}", save_path="helio_image.png"
)

print("Изображение сохранено в helio_image.png")
```

Пример 3: Обнаружение солнечных вспышек

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

Пример 4: Анализ данных Parker Solar Probe

```python
from heliopy import load_psp_sweap, load_psp_fld

# Загрузка данных солнечного ветра
sweap_data = load_psp_sweap("2023-10-15", data_type="spc")

# Загрузка магнитного поля
fld_data = load_psp_fld("2023-10-15", data_type="mag_rtn")

# Анализ параметров солнечного ветра
print(f"Средняя плотность: {sweap_data['density'].mean():.2f} частиц/см³")
print(f"Средняя скорость: {sweap_data['velocity'].mean():.2f} км/с")
print(f"Среднее магнитное поле: {fld_data['Btot'].mean():.2f} нТл")
```

Пример 5: Отслеживание CME

```python
from heliopy import cme_detector, visualization

# Загрузка данных SOHO/LASCO
lasco_data = data_loader.load_soho_lasco("2023-10-15", "C2")

# Обнаружение и отслеживание CME
cme_events = cme_detector.track_cme(lasco_data)

# Визуализация траектории CME
visualization.plot_cme_trajectory(cme_events[0], save_path="cme_trajectory.png")

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
│   │   ├── helioviewer_loader.py    # Данные с Helioviewer
│   │   ├── psp_loader.py            # Данные с Parker Solar Probe
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
│   ├── helioviewer_usage.ipynb     # Работа с данными Helioviewer
│   ├── psp_data_analysis.ipynb     # Анализ данных Parker Solar Probe
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

# Запуск тестов с подробным выводом
pytest -v
```

## 🛠️ Разработка

### Настройка окружения для разработки

```bash
# Клонирование репозитория
git clone https://github.com/QuadDarv1ne/scientific-publications.git
cd scientific-publications/projects/HelioPy

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# или
venv\Scripts\activate     # Windows

# Установка в режиме разработки со всеми зависимостями
pip install -e ".[dev]"
```

### Запуск линтеров и форматтеров

```bash
# Форматирование кода с black
black heliopy/ tests/

# Проверка стиля с ruff
ruff check heliopy/

# Автоматическое исправление проблем с ruff
ruff check heliopy/ --fix

# Проверка типов с mypy
mypy heliopy/ --ignore-missing-imports
```

### Структура коммитов

**Мы следуем [Conventional Commits](https://www.conventionalcommits.org/):**

- `feat:` - новая функциональность
- `fix:` - исправление ошибок
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг без изменения функциональности
- `test:` - добавление/изменение тестов
- `chore:` - обновление зависимостей, конфигурации и т.д.

## 📝 Лицензия

Этот проект лицензирован под `Custom License by Programming School Maestro7IT` - **см. файл** [LICENSE](LICENSE) для деталей.

## 🤝 Участие в разработке

Пожалуйста, прочитайте [CONTRIBUTING.md](CONTRIBUTING.md) для получения инструкций о том, как внести свой вклад в проект.

## 📧 Контакты

- **GitHub Issues:** [https://github.com/QuadDarv1ne/scientific-publications/issues](https://github.com/QuadDarv1ne/scientific-publications/issues)
- **Автор:** `Dupley Maxim Igorevich`

## 🌟 Благодарности

- `SunPy Project` за отличные инструменты для работы с солнечными данными
- `Astropy Community` за фундаментальные астрономические библиотеки
- Всем контрибьюторам проекта

---

**HelioPy** - делаем науку о космической погоде доступной для всех 🌞🚀
