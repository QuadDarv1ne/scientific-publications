
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
