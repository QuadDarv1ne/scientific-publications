# Трекер спутников Starlink - Структура проекта

## Обзор
Этот документ описывает организованную структуру проекта для приложения Starlink Satellite Tracker.

## Структура каталогов
```
starlink_satellite_tracker/
├── README.md
├── requirements.txt
├── config.json
├── starlink_tracker.py          # Главная точка входа
├── PROJECT_STRUCTURE.md         # Этот файл
├── data/
│   └── tle_cache/              # Кэш данных TLE
├── templates/                  # Веб-шаблоны
│   ├── base.html
│   ├── index.html
│   ├── passes.html
│   ├── coverage.html
│   ├── settings.html
│   └── export.html
└── src/                        # Исходный код
   ├── __init__.py
   ├── core/                   # Основная функциональность отслеживания
   │   ├── __init__.py
   │   └── main.py             # Основная логика отслеживания
   ├── web/                    # Веб-интерфейс
   │   ├── __init__.py
   │   └── web_app.py          # Веб-приложение Flask
   ├── utils/                  # Утилиты
   │   ├── __init__.py
   │   ├── config_manager.py   # Централизованное управление конфигурацией
   │   ├── data_processor.py   # Обработка и экспорт данных
   │   ├── notify.py           # Система уведомлений
   │   └── scheduler.py        # Автоматизированный планировщик задач
   └── tests/                  # Тестовые файлы
       ├── __init__.py
       ├── test_tracker.py     # Модульные тесты
       └── различные демо и тестовые скрипты
```

## Описание модулей

### Основной модуль (`src/core/`)
- **main.py**: Содержит основной класс StarlinkTracker с функциональностью отслеживания спутников
- Реализует загрузку, обработку данных TLE и расчет положения спутников
- Обрабатывает загрузку конфигурации и управление ошибками
- Включает механизмы кэширования для оптимизации производительности

### Веб-модуль (`src/web/`)
- **web_app.py**: Веб-приложение на основе Flask с RESTful API
- Предоставляет веб-интерфейс для отслеживания спутников, прогнозирования прохождений и визуализации данных
- Включает конечные точки API для интеграции с другими системами
- Особенности кэширования для ответов API и обработки ошибок

### Модуль утилит (`src/utils/`)
- **config_manager.py**: Централизованное управление конфигурацией с паттерном singleton
- **data_processor.py**: Обработка данных, анализ, фильтрация и функциональность экспорта с кэшированием
- **notify.py**: Система уведомлений с поддержкой электронной почты и Telegram
- **scheduler.py**: Автоматизированный планировщик задач на основе cron-выражений с кэшем выполнения

### Модуль тестов (`src/tests/`)
- Содержит модульные тесты и демонстрационные скрипты
- Включает различные тестовые файлы для проверки функциональности
- Предоставляет примеры использования различных модулей

## Ключевые особенности структуры

1. **Модульная организация**: Четкое разделение задач между основной логикой, веб-интерфейсом и утилитами
2. **Управление конфигурацией**: Централизованный конфигурационный файл, доступный из всех модулей
3. **Хранение данных**: Выделенный каталог данных для кэширования файлов TLE
4. **Веб-шаблоны**: Отдельный каталог для HTML-шаблонов
5. **Тестирование**: Организованный каталог тестов для проверки
6. **Точка входа**: Главный скрипт точки входа для легкого выполнения

## Примеры использования

### Запуск трекера
```bash
python starlink_tracker.py track --help
```

### Запуск веб-интерфейса
```bash
python starlink_tracker.py web
```

### Запуск тестов
```bash
python -m pytest src/tests/ -v
```

## Преимущества этой структуры

1. **Поддерживаемость**: Четкая организация облегчает поиск и изменение определенной функциональности
2. **Масштабируемость**: Модульный дизайн позволяет легко добавлять новые функции
3. **Тестируемость**: Разделение задач облегчает комплексное тестирование
4. **Развертывание**: Организованная структура упрощает развертывание и упаковку
5. **Совместная работа**: Четкая структура помогает членам команды понимать кодовую базу

## Документация API

### API основного трекера (`src/core/main.py`)
- `StarlinkTracker.update_tle_data(force=False)`: Загружает последние данные TLE с Celestrak
- `StarlinkTracker.predict_passes(latitude, longitude, altitude=0, hours_ahead=24, min_elevation=10)`: Прогнозирует прохождения спутников над местоположением
- `StarlinkTracker.visualize_orbits(hours=2)`: Создает 3D-визуализацию орбит спутников
- `StarlinkTracker.start_scheduler()`: Запускает автоматизированные фоновые задачи
- `StarlinkTracker.clear_caches()`: Очищает все внутренние кэши

### API менеджера конфигурации (`src/utils/config_manager.py`)
- `get_config()`: Возвращает полную конфигурацию
- `get_config_section(section_name)`: Возвращает определенную секцию конфигурации
- `get_config_value(section, key, default=None)`: Возвращает определенное значение конфигурации

### API процессора данных (`src/utils/data_processor.py`)
- `DataProcessor.load_satellite_data(filename=None)`: Загружает данные спутников из файлов TLE
- `DataProcessor.filter_satellites(satellites, criteria=None)`: Фильтрует спутники по критериям
- `DataProcessor.export_to_csv(data, filename)`: Экспортирует данные в формат CSV
- `DataProcessor.export_to_json(data, filename)`: Экспортирует данные в формат JSON
- `DataProcessor.analyze_constellation(satellites)`: Выполняет базовый анализ созвездия

### API планировщика (`src/utils/scheduler.py`)
- `StarlinkScheduler.start_scheduler()`: Запускает фоновый планировщик
- `StarlinkScheduler.stop_scheduler()`: Останавливает планировщик
- `StarlinkScheduler.setup_scheduled_tasks()`: Настраивает запланированные задачи
- `StarlinkScheduler.get_scheduled_jobs()`: Возвращает информацию о запланированных задачах

### API системы уведомлений (`src/utils/notify.py`)
- `NotificationSystem.send_email_notification(subject, message, recipient)`: Отправляет уведомления по электронной почте
- `NotificationSystem.send_telegram_notification(message)`: Отправляет уведомления через Telegram
- `NotificationSystem.notify_upcoming_pass(satellite_name, pass_time, max_elevation, azimuth)`: Отправляет уведомление о прохождении спутника

### API веб-приложения (`src/web/web_app.py`)
- `GET /api/satellites`: Возвращает текущие позиции спутников
- `GET /api/passes`: Возвращает прогнозируемые прохождения спутников
- `GET /api/coverage`: Возвращает данные о глобальном покрытии
- `GET /api/export/<format>`: Экспортирует данные в указанном формате (json, csv)
- `POST /api/cache/clear`: Очищает кэш API