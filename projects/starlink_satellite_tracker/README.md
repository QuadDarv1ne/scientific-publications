# 🛰️ Трекер и визуализатор спутников Starlink

![Предварительный просмотр трекера Starlink](https://via.placeholder.com/800x400?text=Starlink+Tracker+Preview) <!-- Замените на реальный скриншот -->

**Система отслеживания и визуализации спутников SpaceX Starlink в реальном времени**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/starlink-tracker?style=social)](https://github.com/yourusername/starlink-tracker)

## 🚀 Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url>

# Установка зависимостей
pip install -r requirements.txt

# Запуск трекера
python starlink_tracker.py track --help

# Запуск веб-интерфейса
python starlink_tracker.py web

# Или запуск напрямую из исходных каталогов
python src/core/main.py --help
python src/web/web_app.py
```

## 📖 Описание

Трекер и визуализатор спутников Starlink — это Python-приложение для отслеживания спутников Starlink в реальном времени с возможностью 3D-визуализации их орбит и прогнозирования прохождений над вашим местоположением. Проект использует астрономические вычисления для точного расчета позиций спутников и предоставляет интерактивные визуализации для лучшего понимания космического созвездия.

**Основные возможности:**
- 📡 Автоматическая загрузка актуальных данных TLE (Two-Line Elements) с Celestrak
- 🌍 Точные расчеты положения спутников с использованием библиотеки Skyfield
- 🗺️ Интерактивная 3D-визуализация орбит спутников
- 📍 Прогнозирование видимости спутников над вашим местоположением
- 🔔 Уведомления о прохождениях спутников над вашим регионом
- 📊 Экспорт данных в CSV/JSON для дальнейшего анализа
- 🌐 Визуализация покрытия Starlink на карте мира
- 🎨 Расширенные возможности визуализации с помощью Plotly и Matplotlib
- 🤖 Автоматизированное планирование задач с помощью cron-выражений
- 🧠 Машинное обучение для улучшенных прогнозов прохождений
- 🕵️‍♂️ Обнаружение аномалий в поведении спутников
- 📱 Дополненная реальность для отслеживания спутников в реальном времени

## 🚀 Возможности

### 📡 Автоматическое обновление данных
- Ежедневная загрузка свежих данных TLE с официальных источников
- Кэширование данных для автономной работы
- Обработка ошибок при недоступности источников
- Резервные URL для устойчивого получения данных

### 🌍 Расчет видимости
- Определение времени восхода и захода спутников
- Расчет высоты и азимута для оптимального наблюдения
- Фильтрация спутников по минимальной высоте над горизонтом
- Учет местного времени и часовых поясов

### 🎨 Визуализация
- **3D орбиты**: Интерактивная визуализация в matplotlib/plotly
- **Карта покрытия**: Отображение текущих позиций спутников на карте мира
- **Графики высоты**: Визуализация траекторий прохождения над точкой наблюдения
- **Анимация движения**: Динамическое отображение движения спутников
- **Вид дополненной реальности**: Отслеживание спутников в реальном времени с помощью камеры устройства
- **Прогнозы на основе машинного обучения**: Улучшенные прогнозы прохождений с помощью ML

### 🔔 Система уведомлений
- Уведомления по электронной почте о прохождениях спутников
- Push-уведомления через Telegram-бот
- Push-уведомления через сервис Pushover
- Настройка критериев уведомлений (минимальная высота, яркость, скорость)
- Оповещения об обнаружении аномалий в поведении спутников

## ⚙️ Требования

### Системные требования
- Python 3.8 или новее
- 2 ГБ ОЗУ
- 500 МБ свободного места на диске
- Подключение к интернету для загрузки данных TLE

### Зависимости Python
```bash
skyfield
matplotlib
numpy
pandas
requests
flask
geopy
plotly
dash
schedule
python-telegram-bot
```

Установка зависимостей:
```bash
pip install -r requirements.txt
```

## 📚 Документация модулей

### Основной трекер (`src/core/main.py`)
Основной модуль, отвечающий за отслеживание спутников и вычисления.

**Основные методы:**
- `update_tle_data()`: Загружает последние данные TLE с Celestrak
- `predict_passes()`: Прогнозирует прохождения спутников над местоположением
- `visualize_orbits()`: Создает 3D-визуализацию орбит спутников
- `start_scheduler()`: Запускает автоматизированные фоновые задачи
- `clear_caches()`: Очищает все внутренние кэши

**Пример использования:**
```python
from src.core.main import StarlinkTracker

# Инициализация трекера
tracker = StarlinkTracker()

# Обновление данных спутников
satellites = tracker.update_tle_data()

# Прогноз прохождений для Москвы
passes = tracker.predict_passes(latitude=55.7558, longitude=37.6173)

# Визуализация орбит
tracker.visualize_orbits()
```

### Менеджер конфигурации (`src/utils/config_manager.py`)
Централизованная система управления конфигурацией с использованием паттерна singleton.

**Основные методы:**
- `get_config()`: Возвращает полную конфигурацию
- `get_config_section()`: Возвращает определенную секцию конфигурации
- `get_config_value()`: Возвращает определенное значение конфигурации
- `reload_config()`: Перезагружает конфигурацию из файла

**Структура файла конфигурации:**
```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7,
    "backup_urls": [
      "https://celestrak.org/NORAD/elements/starlink.txt",
      "https://www.celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=csv"
    ]
  },
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark",
    "plotly_3d": true,
    "matplotlib_2d": true
  },
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  },
  "observer": {
    "default_latitude": 55.7558,
    "default_longitude": 37.6173,
    "default_altitude": 0,
    "timezone": "Europe/Moscow"
  },
  "notifications": {
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "",
      "password": "",
      "recipient": ""
    },
    "telegram": {
      "enabled": false,
      "bot_token": "",
      "chat_id": ""
    },
    "min_elevation": 10,
    "min_brightness": -1,
    "min_velocity": 0,
    "advance_notice_minutes": 30,
    "excluded_satellites": [],
    "excluded_patterns": ["DEBRIS", "TEST"],
    "included_satellites": [],
    "included_patterns": []
  },
  "pushover": {
    "enabled": false,
    "user_key": "",
    "api_token": ""
  },
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

### Процессор данных (`src/utils/data_processor.py`)
Обрабатывает анализ данных, фильтрацию и экспорт с кэшированием.

**Основные методы:**
- `load_satellite_data()`: Загружает данные спутников из файлов TLE
- `filter_satellites()`: Фильтрует спутники по критериям
- `export_to_csv()`: Экспортирует данные в формат CSV
- `export_to_json()`: Экспортирует данные в формат JSON
- `analyze_constellation()`: Выполняет базовый анализ созвездия
- `calculate_satellite_statistics()`: Вычисляет статистику для прохождений спутников
- `clear_cache()`: Очищает кэш процессора данных

**Пример использования:**
```python
from src.utils.data_processor import DataProcessor

# Инициализация процессора
processor = DataProcessor()

# Загрузка данных спутников
satellites = processor.load_satellite_data()

# Анализ созвездия
stats = processor.analyze_constellation(satellites)

# Экспорт в CSV
processor.export_to_csv(satellites, "starlink_data.csv")
```

### Планировщик (`src/utils/scheduler.py`)
Автоматизированный планировщик задач на основе cron-выражений с кэшированием выполнения.

**Основные методы:**
- `start_scheduler()`: Запускает фоновый планировщик
- `stop_scheduler()`: Останавливает планировщик
- `setup_scheduled_tasks()`: Настраивает запланированные задачи
- `get_scheduled_jobs()`: Возвращает информацию о запланированных задачах
- `clear_cache()`: Очищает кэш выполнения планировщика

**Поддерживаемые cron-выражения:**
- `0 0 */6 * *`: Каждые 6 часов
- `*/30 * * * *`: Каждые 30 минут
- `*/15 * * * *`: Каждые 15 минут
- `0 0 * * *`: Ежедневно в полночь
- `0 * * * *`: Ежечасно

**Пример конфигурации планировщика:**
```python
# В config.json
{
    "schedule": {
        "tle_update_cron": "0 0 */6 * *",
        "prediction_update_cron": "*/30 * * * *",
        "notification_check_cron": "*/15 * * * *",
    }
}
```

### Система уведомлений (`src/utils/notify.py`)
Отправляет оповещения о предстоящих прохождениях спутников по электронной почте или через Telegram.

**Основные методы:**
- `send_email_notification()`: Отправляет уведомления по электронной почте
- `send_telegram_notification()`: Отправляет уведомления через Telegram
- `send_pushover_notification()`: Отправляет уведомления через Pushover
- `notify_upcoming_pass()`: Отправляет уведомление о прохождении спутника

**Конфигурация:**
```json
{
  "notifications": {
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "",
      "password": "",
      "recipient": ""
    },
    "telegram": {
      "enabled": false,
      "bot_token": "",
      "chat_id": ""
    },
    "min_elevation": 10,
    "min_brightness": -1,
    "min_velocity": 0,
    "advance_notice_minutes": 30,
    "excluded_satellites": [],
    "excluded_patterns": ["DEBRIS", "TEST"],
    "included_satellites": [],
    "included_patterns": []
  }
}
```

**Фильтрация уведомлений:**
- `min_elevation`: Минимальный угол возвышения для уведомлений (по умолчанию: 10°)
- `min_brightness`: Минимальная яркость (величина) для уведомлений (по умолчанию: -1)
- `min_velocity`: Минимальная скорость для уведомлений (по умолчанию: 0 км/с)
- `excluded_satellites`: Список конкретных названий спутников для исключения из уведомлений
- `excluded_patterns`: Список шаблонов для исключения из уведомлений (например, "DEBRIS" исключает все спутники-обломки)
- `included_satellites`: Список конкретных названий спутников для включения в уведомления (пустой список = все спутники)
- `included_patterns`: Список шаблонов для включения в уведомления (пустой список = все спутники)
- `advance_notice_minutes`: Время до прохождения для отправки уведомления (по умолчанию: 30 минут)

**Настройка уведомлений по электронной почте:**
```python
# Включение уведомлений по электронной почте в config.json
{
    "notifications": {
        "email": {
            "enabled": true,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your_email@gmail.com",
            "password": "your_app_password",
            "recipient": "recipient@example.com",
        }
    }
}
```

**Настройка уведомлений через Telegram:**
```python
# Включение уведомлений через Telegram в config.json
{
    "notifications": {
        "telegram": {"enabled": true, "bot_token": "your_bot_token", "chat_id": "your_chat_id"}
    }
}
```

**Настройка уведомлений через Pushover:**
```python
# Включение уведомлений через Pushover в config.json
{"pushover": {"enabled": true, "user_key": "your_user_key", "api_token": "your_api_token"}}
```

### Веб-приложение (`src/web/web_app.py`)
Веб-интерфейс на основе Flask с RESTful API и кэшированием.

**Расширенные возможности визуализации:**
- Интерактивная 3D-визуализация орбит с использованием Plotly
- Информационная панель отслеживания спутников в реальном времени
- Настраиваемые параметры визуализации (период времени, количество спутников)
- Параметры цветовой схемы для лучшей визуализации
- Отдельная страница визуализации (`/visualization`) с расширенными элементами управления
- Карта спутников в реальном времени (`/map`) с отображением текущих позиций спутников
- Страница статистики (`/statistics`) с анализом прохождений спутников
- Вид дополненной реальности (`/ar`) для отслеживания спутников в реальном времени
- Панель обнаружения аномалий для мониторинга поведения спутников
- Система прогнозирования на основе машинного обучения для улучшенного прогнозирования прохождений

**Конечные точки API:**
- `GET /api/satellites`: Возвращает текущие позиции спутников
- `GET /api/passes`: Возвращает прогнозируемые прохождения спутников
- `GET /api/coverage`: Возвращает данные о глобальном покрытии
- `GET /api/export/<format>`: Экспортирует данные в указанном формате (json, csv)
- `GET /api/visualization/orbits`: Возвращает данные для интерактивной 3D-визуализации орбит
- `GET /api/statistics`: Возвращает статистический анализ прохождений спутников
- `GET /api/anomalies`: Возвращает обнаруженные аномалии спутников
- `GET /api/predictions/ml`: Возвращает прогнозы прохождений спутников на основе машинного обучения
- `POST /api/cache/clear`: Очищает кэш API

**Веб-страницы:**
- `/` - Главная информационная панель с текущими позициями спутников
- `/passes` - Календарь прохождений над вашим местоположением
- `/coverage` - Карта мира с покрытием Starlink
- `/map` - Карта спутников в реальном времени с интерактивной картой
- `/visualization` - 3D-визуализация орбит с расширенными элементами управления
- `/statistics` - Статистический анализ прохождений спутников
- `/ar` - Вид дополненной реальности для отслеживания спутников в реальном времени
- `/settings` - Настройки наблюдателя и уведомлений
- `/export` - Экспорт данных в различных форматах

**Примеры использования API:**
```bash
# Получение текущих позиций спутников
curl http://localhost:5000/api/satellites

# Получение прохождений для определенного местоположения
curl "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060&hours=48"

# Экспорт данных в JSON
curl http://localhost:5000/api/export/json

# Получение аномалий спутников
curl http://localhost:5000/api/anomalies

# Получение прогнозов на основе ML
curl http://localhost:5000/api/predictions/ml

# Очистка кэша
curl -X POST http://localhost:5000/api/cache/clear
```

## 🖥️ Веб-интерфейс

При запуске web_app.py доступны следующие страницы:

- `/` - Главная информационная панель с текущими позициями спутников
- `/passes` - Календарь прохождений над вашим местоположением
- `/coverage` - Карта мира с покрытием Starlink
- `/settings` - Настройки наблюдателя и уведомлений
- `/export` - Экспорт данных в различных форматах

### Запуск веб-интерфейса

```bash
# Использование основного скрипта
python starlink_tracker.py web

# Или напрямую из каталога web
python src/web/web_app.py
```

После запуска откройте браузер по адресу http://localhost:5000

## 🧪 Тестирование

Проект включает комплексный набор тестов:

```bash
# Запуск всех тестов
python -m pytest src/tests/ -v

# Запуск определенного модуля тестов
python src/tests/test_config_manager.py

# Запуск тестов с покрытием
python -m pytest src/tests --cov=src --cov-report=html

# Запуск определенного класса тестов
python -m pytest src/tests/test_core_tracker.py::TestStarlinkTracker -v
```

**Расширенное покрытие тестами:**
- Тестирование пользовательских исключений
- Расширенные тесты кэширования процессора данных
- Тесты фильтрации уведомлений
- Валидация основной функциональности

## 🛠️ Аргументы командной строки

### Аргументы трекера
```bash
usage: main.py [-h] [--update] [--visualize] [--notify] [--schedule] [--debug]

Трекер спутников Starlink

optional arguments:
  -h, --help      показать это справочное сообщение и выйти
  --update        Принудительное обновление данных TLE
  --visualize     Показать 3D-визуализацию (по умолчанию: False)
  --notify        Отправить уведомления о предстоящих прохождениях
  --schedule      Запустить планировщик для автоматизированных задач
  --debug         Включить ведение журнала отладки
```

### Примеры использования

```bash
# Обновление данных TLE и показ предстоящих прохождений
python starlink_tracker.py track --update

# Показ 3D-визуализации орбит
python starlink_tracker.py track --visualize

# Запуск планировщика для автоматизированных задач
python starlink_tracker.py track --schedule

# Включение режима отладки
python starlink_tracker.py track --debug

# Или запуск напрямую из каталога src/core
python src/core/main.py --update
```

## 📊 Пример отчета о прохождениях

```
Отчет о прохождениях Starlink для Московской обсерватории
Сгенерировано: 2025-11-10 15:30:00 MSK
Период: Следующие 24 часа

┌───────────────┬────────────┬────────────┬────────────┬──────────────┐
│ ID спутника   │ Время      │ Макс.      │ Длитель-   │ Макс.        │
│               │ начала     │ высота     │ ность      │ возвышение   │
├───────────────┼────────────┼────────────┼────────────┼──────────────┤
│ STARLINK-1234 │ 18:45:23   │ 65°        │ 4m 12s     │ 42°          │
│ STARLINK-5678 │ 19:12:08   │ 78°        │ 5m 37s     │ 58°          │
│ STARLINK-9012 │ 20:03:45   │ 45°        │ 3m 21s     │ 28°          │
└───────────────┴────────────┴────────────┴────────────┴──────────────┘
```

## 🔧 Конфигурация

### Файл конфигурации (`config.json`)

```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7
  },
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark"
  },
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  }
}
```

## 📈 Оптимизация производительности

Система включает несколько оптимизаций производительности:

1. **Расширенное кэширование**: 
   - Кэширование данных TLE в памяти с истечением срока действия
   - Кэширование ответов API в веб-интерфейсе
   - Кэширование результатов прогнозирования
   - Кэширование процессора данных с вытеснением LRU и TTL
   - Периодическая очистка кэша для предотвращения утечек памяти

2. **Обработка данных**:
   - Эффективный парсинг TLE
   - Селективная обработка спутников (первые N спутников)
   - Сжатый экспорт данных для больших наборов данных
   - Расширенные возможности фильтрации

3. **Оптимизация планировщика**:
   - Кэш выполнения для предотвращения повторных запусков задач
   - Настраиваемое планирование на основе cron-выражений
   - Фоновая многопоточность для неблокирующих операций
   - Автоматизированная проверка уведомлений с фильтрацией

4. **Веб-интерфейс**:
   - Интерактивная 3D-визуализация орбит с Plotly
   - Информационная панель отслеживания спутников в реальном времени
   - Настраиваемые параметры визуализации
   - Визуализация спутников в реальном времени на карте
   - Статистический анализ прохождений спутников
   - Адаптивный дизайн для всех устройств

## 🤝 Участие в разработке

1. Сделайте форк репозитория
2. Создайте ветку с вашей функцией (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте ветку (`git push origin feature/AmazingFeature`)
5. Откройте пул-реквест

## 📄 Лицензия

Этот проект лицензирован по лицензии MIT - смотрите файл [LICENSE](LICENSE) для получения подробной информации.

## 📞 Контакты

Ссылка на проект: [https://github.com/yourusername/starlink-tracker](https://github.com/yourusername/starlink-tracker)