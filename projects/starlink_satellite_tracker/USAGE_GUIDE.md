# 🛰️ Трекер спутников Starlink - Руководство по использованию

Это руководство содержит подробные инструкции по использованию всех функций Трекера спутников Starlink, включая недавно расширенные возможности.

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

## 🖥️ Использование веб-интерфейса

### Главная информационная панель (`/`)

Главная информационная панель предоставляет обзор:
- Текущего статуса отслеживания спутников
- Следующего видимого прохождения спутника
- Последней активности (предстоящие прохождения)

### Страница прохождений (`/passes`)

Просмотр и прогнозирование прохождений спутников над вашим местоположением:
- Настройка местоположения наблюдателя (широта, долгота, высота)
- Установка периода времени для прогнозов (1-168 часов)
- Просмотр подробной информации о прохождении (время, возвышение, азимут, расстояние)

### Страница визуализации (`/visualization`)

Интерактивная 3D-визуализация орбит спутников:
- Настройка периода времени (1-24 часа)
- Выбор количества спутников для отображения (5-30)
- Выбор цветовых схем (по умолчанию, радужная, на основе скорости)
- Вращение, масштабирование и панорамирование 3D-вида

### Страница покрытия (`/coverage`)

Просмотр глобального покрытия созвездия Starlink:
- Региональная статистика покрытия
- Информация о статусе созвездия

### Страница настроек (`/settings`)

Настройка всех системных параметров:
- Предпочтения местоположения наблюдателя
- Настройки уведомлений (электронная почта, Telegram)
- Системная конфигурация (источники данных, планировщик)

### Страница экспорта (`/export`)

Экспорт данных спутников в различных форматах:
- Формат JSON или CSV
- Выбор данных для включения (данные TLE, прогнозы)
- Выбор диапазона дат для экспорта

## 📊 Использование API

### Основные конечные точки API

#### Получение позиций спутников
```bash
# Получение текущих позиций спутников
curl http://localhost:5000/api/satellites
```

#### Получение прогнозируемых прохождений
```bash
# Получение прохождений для определенного местоположения
curl "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060&hours=48"
```

#### Получение глобального покрытия
```bash
# Получение данных о глобальном покрытии
curl http://localhost:5000/api/coverage
```

#### Экспорт данных
```bash
# Экспорт данных в JSON
curl http://localhost:5000/api/export/json

# Экспорт данных в CSV
curl http://localhost:5000/api/export/csv
```

#### Визуализация орбит
```bash
# Получение данных для интерактивной 3D-визуализации орбит
curl "http://localhost:5000/api/visualization/orbits?hours=2&satellites=10"
```

#### Очистка кэша
```bash
# Очистка всех кэшированных данных
curl -X POST http://localhost:5000/api/cache/clear
```

## ⚙️ Конфигурация

### Структура файла конфигурации

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
    "advance_notice_minutes": 30,
    "excluded_satellites": [],
    "excluded_patterns": ["DEBRIS", "TEST"]
  },
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

## 📧 Система уведомлений

### Уведомления по электронной почте

Для включения уведомлений по электронной почте настройте раздел электронной почты в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json):

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "recipient": "recipient@example.com"
    }
  }
}
```

### Уведомления через Telegram

Для включения уведомлений через Telegram настройте раздел Telegram в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json):

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token",
      "chat_id": "your_chat_id"
    }
  }
}
```

### Фильтрация уведомлений

Система уведомлений включает расширенные возможности фильтрации:

- **Минимальное возвышение**: Уведомлять только о прохождениях выше указанного угла возвышения
- **Минимальная яркость**: Уведомлять только о спутниках ярче указанной величины
- **Исключенные спутники**: Пропускать уведомления для определенных названий спутников
- **Исключенные шаблоны**: Пропускать уведомления для спутников, соответствующих определенным шаблонам

## 📈 Оптимизация производительности

### Расширенное кэширование

Система реализует несколько уровней кэширования:

1. **Кэширование данных TLE**: Данные спутников кэшируются с истечением срока действия
2. **Кэширование ответов API**: Ответы веб-API кэшируются для снижения вычислительной нагрузки
3. **Кэширование прогнозов**: Прогнозы прохождений кэшируются для избежания повторных вычислений
4. **Кэширование процессора данных**: Операции экспорта кэшируются с вытеснением LRU

### Управление памятью

- Периодическая очистка кэша для предотвращения утечек памяти
- Настраиваемые размеры кэша и значения TTL
- Автоматическое удаление истекших записей

## 🧪 Тестирование

### Запуск тестов

```bash
# Запуск всех тестов
python -m pytest src/tests/ -v

# Запуск определенного модуля тестов
python src/tests/test_config_manager.py

# Запуск тестов с покрытием
python -m pytest src/tests/ --cov=src --cov-report=html

# Запуск определенного класса тестов
python -m pytest src/tests/test_core_tracker.py::TestStarlinkTracker -v
```

### Покрытие тестами

Набор тестов включает:
- Тесты основной функциональности трекера
- Тесты менеджера конфигурации
- Тесты процессора данных
- Тесты системы уведомлений
- Тесты планировщика
- Тесты веб-приложения
- Тесты пользовательских исключений
- Расширенные тесты кэширования

## 🛠️ Использование командной строки

### Команды трекера

```bash
# Обновление данных TLE и показ предстоящих прохождений
python starlink_tracker.py track --update

# Показ 3D-визуализации орбит
python starlink_tracker.py track --visualize

# Запуск планировщика для автоматизированных задач
python starlink_tracker.py track --schedule

# Включение режима отладки
python starlink_tracker.py track --debug

# Отправка уведомлений о предстоящих прохождениях
python starlink_tracker.py track --notify
```

### Команды веб-интерфейса

```bash
# Запуск веб-интерфейса
python starlink_tracker.py web

# Запуск веб-интерфейса с ведением журнала отладки
python starlink_tracker.py web --debug
```

## 🤖 Конфигурация планировщика

Планировщик поддерживает настраиваемые cron-выражения:

- `0 0 */6 * *`: Каждые 6 часов (обновления TLE)
- `*/30 * * * *`: Каждые 30 минут (обновления прогнозов)
- `*/15 * * * *`: Каждые 15 минут (проверки уведомлений)

Настройте их в разделе [schedule](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/src/utils/scheduler.py#L27-L27) файла [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json).

## 📊 Экспорт данных

### Форматы экспорта

- **JSON**: Структурированный экспорт данных с метаданными
- **CSV**: Табличный экспорт данных для приложений электронных таблиц

### Параметры экспорта

- Включение данных TLE
- Включение результатов прогнозирования
- Автоматическое сжатие больших файлов
- Выбор диапазонов дат для экспорта

## 🔧 Устранение неполадок

### Распространенные проблемы

1. **Данные TLE не обновляются**: Проверьте подключение к интернету и URL источников данных
2. **Визуализация не работает**: Убедитесь, что установлены matplotlib и plotly
3. **Уведомления не отправляются**: Проверьте конфигурацию и учетные данные
4. **Планировщик не работает**: Проверьте cron-выражения и системное время

### Отладка

Включите ведение журнала отладки для получения подробной информации:

```bash
python starlink_tracker.py track --debug
python starlink_tracker.py web --debug
```

## 📈 Советы по производительности

1. **Управление кэшем**: Регулярно очищайте кэш, если использование памяти велико
2. **Выбор спутников**: Ограничьте количество спутников для визуализации
3. **Частота обновления**: Настройте интервалы планировщика в соответствии с потребностями
4. **Хранение данных**: Настройте соответствующие сроки истечения кэша

## 🤝 Участие в разработке

1. Сделайте форк репозитория
2. Создайте ветку с вашей функцией (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте ветку (`git push origin feature/AmazingFeature`)
5. Откройте пул-реквест

## 📄 Лицензия

Этот проект лицензирован по лицензии MIT - смотрите файл [LICENSE](LICENSE) для получения подробной информации.

## Содержание
1. [Установка](#установка)
2. [Базовое использование](#базовое-использование)
3. [Конфигурация](#конфигурация)
4. [Интерфейс командной строки](#интерфейс-командной-строки)
5. [Веб-интерфейс](#веб-интерфейс)
6. [Использование API](#использование-api)
7. [Настройка уведомлений](#настройка-уведомлений)
8. [Экспорт данных](#экспорт-данных)
9. [Расширенные функции](#расширенные-функции)
10. [Устранение неполадок](#устранение-неполадок)

## Установка

### Предварительные требования
- Python 3.8 или новее
- Менеджер пакетов pip
- Подключение к интернету для загрузки данных TLE

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd starlink_satellite_tracker
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Проверьте установку:
```bash
python starlink_tracker.py track --help
```

## Базовое использование

### Быстрый старт
Для быстрого просмотра прохождений спутников над вашим местоположением:

```bash
python starlink_tracker.py track
```

Это выполнит:
1. Загрузку последних данных TLE (если необходимо)
2. Прогнозирование прохождений над местоположением по умолчанию (Москва)
3. Отображение результатов

### Пользовательское местоположение
Для прогнозирования прохождений для пользовательского местоположения:

```bash
python starlink_tracker.py track --update
```

Затем измените файл [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json), чтобы установить ваше местоположение:

```json
{
  "observer": {
    "default_latitude": 40.7128,
    "default_longitude": -74.0060,
    "default_altitude": 0,
    "timezone": "America/New_York"
  }
}
```

## Конфигурация

### Структура файла конфигурации
Основной файл конфигурации - [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json) в корне проекта. Вот разбивка всех параметров конфигурации:

#### Источники данных
```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7,
    "backup_urls": [
      "https://celestrak.org/NORAD/elements/starlink.txt"
    ]
  }
}
```

#### Настройки визуализации
```json
{
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark",
    "plotly_3d": true,
    "matplotlib_2d": true
  }
}
```

#### Планирование
```json
{
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  }
}
```

#### Настройки наблюдателя
```json
{
  "observer": {
    "default_latitude": 55.7558,
    "default_longitude": 37.6173,
    "default_altitude": 0,
    "timezone": "Europe/Moscow"
  }
}
```

#### Уведомления
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
    "advance_notice_minutes": 30
  }
}
```

#### Настройки экспорта
```json
{
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

## Интерфейс командной строки

### Основные команды

#### Команда Track
```bash
python starlink_tracker.py track [options]
```

Параметры:
- `--update`: Принудительное обновление данных TLE
- `--visualize`: Показать 3D-визуализацию
- `--notify`: Отправить уведомления о предстоящих прохождениях
- `--schedule`: Запустить планировщик для автоматизированных задач
- `--debug`: Включить ведение журнала отладки

#### Команда Web
```bash
python starlink_tracker.py web
```

Запускает веб-интерфейс по адресу http://localhost:5000

### Примеры

#### Обновление данных TLE и показ прохождений
```bash
python starlink_tracker.py track --update
```

#### Показ 3D-визуализации
```bash
python starlink_tracker.py track --visualize
```

#### Запуск автоматизированного планировщика
```bash
python starlink_tracker.py track --schedule
```

#### Включение режима отладки
```bash
python starlink_tracker.py track --debug
```

## Веб-интерфейс

### Запуск веб-интерфейса
```bash
python starlink_tracker.py web
```

Или напрямую:
```bash
python src/web/web_app.py
```

### Веб-страницы

#### Информационная панель (`/`)
Главная информационная панель, показывающая:
- Текущее количество спутников
- Следующее прогнозируемое прохождение
- Статус системы

#### Прохождения (`/passes`)
Подробный просмотр предстоящих прохождений спутников:
- Таблица прохождений с временами и позициями
- Фильтрация по периоду времени
- Прогнозы для конкретного местоположения

#### Покрытие (`/coverage`)
Карта мира, показывающая:
- Текущее покрытие созвездия Starlink
- Региональную статистику
- Визуализацию плотности спутников

#### Настройки (`/settings`)
Параметры конфигурации:
- Настройки местоположения наблюдателя
- Предпочтения уведомлений
- Системная конфигурация

#### Экспорт (`/export`)
Функциональность экспорта данных:
- Экспорт в формате JSON или CSV
- Выбор типов данных для включения
- Загрузка экспортированных файлов

### Конечные точки API

#### GET `/api/satellites`
Возвращает текущие позиции спутников.

Пример:
```bash
curl http://localhost:5000/api/satellites
```

Ответ:
```json
{
  "satellites": [
    {
      "name": "STARLINK-1234",
      "id": "1234"
    }
  ],
  "count": 100,
  "updated": "2025-11-10T15:30:00"
}
```

#### GET `/api/passes`
Возвращает прогнозируемые прохождения спутников.

Пример:
```bash
curl "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060&hours=48"
```

Ответ:
```json
{
  "passes": [
    {
      "satellite": "STARLINK-1234",
      "time": "2025-11-10T18:45:23",
      "altitude": 65.5,
      "azimuth": 42.3,
      "distance": 350.2
    }
  ],
  "count": 15,
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "period_hours": 48
}
```

#### GET `/api/coverage`
Возвращает данные о глобальном покрытии.

Пример:
```bash
curl http://localhost:5000/api/coverage
```

Ответ:
```json
{
  "regions": [
    {
      "name": "North America",
      "satellite_count": 1500,
      "coverage_percentage": 98.5
    }
  ],
  "total_satellites": 2500,
  "global_coverage": 92.1
}
```

#### GET `/api/export/<format>`
Экспортирует данные в указанном формате.

Пример:
```bash
curl http://localhost:5000/api/export/json
curl http://localhost:5000/api/export/csv
```

#### POST `/api/cache/clear`
Очищает кэш API.

Пример:
```bash
curl -X POST http://localhost:5000/api/cache/clear
```

## Использование API

### Примеры API на Python

#### Базовое отслеживание
```python
from src.core.main import StarlinkTracker

# Инициализация трекера
tracker = StarlinkTracker()

# Обновление данных спутников
satellites = tracker.update_tle_data()

# Прогнозирование прохождений для Нью-Йорка
passes = tracker.predict_passes(latitude=40.7128, longitude=-74.0060, hours_ahead=48)

# Вывод результатов
for p in passes[:10]:
    print(f"{p['satellite']}: {p['time']} at {p['altitude']:.1f}°")
```

#### Обработка данных
```python
from src.utils.data_processor import DataProcessor

# Инициализация процессора
processor = DataProcessor()

# Загрузка данных спутников
satellites = processor.load_satellite_data()

# Анализ созвездия
stats = processor.analyze_constellation(satellites)
print(f"Total satellites: {stats['total_satellites']}")

# Экспорт в CSV
processor.export_to_csv(satellites, "starlink_data.csv")
```

#### Управление конфигурацией
```python
from src.utils.config_manager import get_config, get_config_value

# Получение полной конфигурации
config = get_config()

# Получение определенных значений
latitude = get_config_value("observer", "default_latitude", 0.0)
celestrak_url = get_config_value("data_sources", "celestrak_url")
```

#### Планирование
```python
from src.utils.scheduler import StarlinkScheduler
from src.core.main import StarlinkTracker

# Инициализация трекера и планировщика
tracker = StarlinkTracker()
scheduler = StarlinkScheduler(tracker=tracker)

# Запуск планировщика
if scheduler.start_scheduler():
    print("Scheduler started successfully")
else:
    print("Failed to start scheduler")
```

## Настройка уведомлений

### Уведомления по электронной почте

1. Включите уведомления по электронной почте в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json):
```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "recipient": "recipient@example.com"
    }
  }
}
```

2. Для Gmail вам нужно:
   - Включить двухфакторную аутентификацию
   - Сгенерировать пароль приложения
   - Использовать пароль приложения вместо обычного пароля

### Уведомления через Telegram

1. Создайте Telegram-бота:
   - Поговорите с @BotFather в Telegram
   - Используйте команду `/newbot`
   - Следуйте инструкциям, чтобы получить токен вашего бота

2. Получите ваш ID чата:
   - Поговорите со своим новым ботом
   - Отправьте любое сообщение
   - Посетите `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Найдите ваш ID чата в ответе

3. Настройте в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json):
```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token_here",
      "chat_id": "your_chat_id_here"
    }
  }
}
```

### Тестирование уведомлений
```python
from src.utils.notify import NotificationSystem

# Инициализация системы уведомлений
notifier = NotificationSystem()

# Отправка тестового уведомления
success = notifier.notify_upcoming_pass(
    "STARLINK-TEST", datetime.now() + timedelta(minutes=30), 65.5, 42.3
)

if success:
    print("Notification sent successfully")
else:
    print("Failed to send notification")
```

## Экспорт данных

### Форматы экспорта

#### Экспорт JSON
```python
from src.utils.data_processor import DataProcessor

processor = DataProcessor()
satellites = processor.load_satellite_data()

# Экспорт в JSON
processor.export_to_json(satellites, "starlink_export.json")
```

Структура результирующего JSON:
```json
{
  "satellites": [
    {
      "name": "STARLINK-1234",
      "line1": "1 12345U 12345ABC  23156.12345678  .00000000  00000-0  00000+0 0  1234",
      "line2": "2 12345  53.0000 123.4567 0001234 321.4567 123.4567 15.23456789 12345"
    }
  ],
  "exported": "2025-11-10T15:30:00",
  "count": 100,
  "version": "1.0"
}
```

#### Экспорт CSV
```python
# Экспорт в CSV
processor.export_to_csv(satellites, "starlink_export.csv")
```

### Веб-экспорт
Через веб-интерфейс:
1. Перейдите к `/export`
2. Выберите формат экспорта (JSON/CSV)
3. Нажмите кнопку экспорта
4. Загрузите файл

### API-экспорт
```
# Экспорт через API
curl http://localhost:5000/api/export/json -o starlink_data.json
curl http://localhost:5000/api/export/csv -o starlink_data.csv
```

## Расширенные функции

### Пользовательское планирование
Планировщик поддерживает cron-выражения для пользовательской автоматизации:

```json
{
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",      // Каждые 6 часов
    "prediction_update_cron": "*/30 * * * *", // Каждые 30 минут
    "notification_check_cron": "*/15 * * * *"  // Каждые 15 минут
  }
}
```

Поддерживаемые cron-шаблоны:
- `0 0 */6 * *`: Каждые 6 часов
- `*/30 * * * *`: Каждые 30 минут
- `*/15 * * * *`: Каждые 15 минут
- `0 0 * * *`: Ежедневно в полночь
- `0 * * * *`: Ежечасно

### Система кэширования
Приложение использует несколько уровней кэширования для производительности:

1. **Кэш TLE**: Кэш данных TLE в памяти (по умолчанию 6 часов)
2. **Кэш прогнозов**: Кэш результатов прогнозирования (по умолчанию 15 минут)
3. **Кэш API**: Кэш ответов веб-API (варьируется по конечной точке)
4. **Кэш процессора данных**: Кэш обработанных данных

Очистите кэши при необходимости:
```python
# Очистка всех кэшей
tracker.clear_caches()

# Очистка кэша API
curl -X POST http://localhost:5000/api/cache/clear
```

### Настройка визуализации
Настройте параметры визуализации в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json):

```json
{
  "visualization": {
    "orbit_points": 200,           // Более детализированные орбиты
    "show_ground_track": false,    // Скрыть наземный след
    "color_scheme": "light",       // Светлая цветовая схема
    "plotly_3d": true,             // Включить 3D-графики
    "matplotlib_2d": false         // Отключить 2D-графики
  }
}
```

## Устранение неполадок

### Распространенные проблемы

#### Сбои загрузки данных TLE
**Симптом**: Ошибка "Failed to download TLE data"
**Решения**:
1. Проверьте подключение к интернету
2. Проверьте URL Celestrak в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json)
3. Проверьте настроены ли резервные URL
4. Убедитесь, что брандмауэр разрешает исходящие соединения

#### Отсутствующие зависимости
**Симптом**: Сообщения ImportError
**Решение**:
```bash
pip install -r requirements.txt
```

#### Ошибки разрешений
**Симптом**: "Permission denied" при создании каталогов кэша
**Решения**:
1. Запустите с соответствующими разрешениями
2. Измените каталог кэша в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json) на доступное для записи место

#### Проблемы с визуализацией
**Симптом**: Ошибка "Matplotlib not installed"
**Решение**:
```bash
pip install matplotlib
```

#### Сбои уведомлений по электронной почте
**Симптом**: Уведомления по электронной почте не отправляются
**Решения**:
1. Проверьте настройки SMTP в [config.json](file:///c%3A/Users/maksi/OneDrive/Documents/GitHub/scientific-publications/projects/starlink_satellite_tracker/config.json)
2. Проверьте имя пользователя/пароль
3. Для Gmail убедитесь, что используется пароль приложения
4. Проверьте адрес электронной почты получателя

#### Сбои уведомлений через Telegram
**Симптом**: Уведомления через Telegram не отправляются
**Решения**:
1. Проверьте токен бота
2. Проверьте ID чата
3. Убедитесь, что бот не заблокирован
4. Установите python-telegram-bot:
   ```bash
   pip install python-telegram-bot
   ```

### Отладка

#### Включение ведения журнала отладки
```bash
python starlink_tracker.py track --debug
```

#### Проверка журналов
Журналы выводятся в консоль по умолчанию. Для ведения журнала в файл измените конфигурацию ведения журнала в каждом модуле.

#### Тестирование отдельных компонентов
```bash
# Тестирование конфигурации
python src/utils/config_manager.py

# Тестирование процессора данных
python src/utils/data_processor.py

# Тестирование планировщика
python src/utils/scheduler.py
```

### Настройка производительности

#### Настройки кэша
Настройте значения TTL кэша в коде в соответствии с вашими потребностями:
- Длинный TTL для менее частых обновлений
- Короткий TTL для быстро меняющихся данных

#### Ограничения обработки спутников
Система обрабатывает ограниченное количество спутников для производительности:
- Измените ограничения спутников в функциях прогнозирования
- Настройте orbit_points для детализации визуализации

#### Использование памяти
Отслеживайте использование памяти с большими наборами данных:
- Периодически очищайте кэши
- Используйте сжатый экспорт для больших файлов
- Отслеживайте системные ресурсы во время работы

### Получение помощи

#### Документация
- README.md: Обзор проекта и быстрый старт
- PROJECT_STRUCTURE.md: Организация кода
- API_DOCUMENTATION.md: Подробная справочная информация по API
- Этот USAGE_GUIDE.md: Комплексные инструкции по использованию

#### Поддержка
Для проблем, не охваченных этим руководством:
1. Проверьте страницу проблем на GitHub
2. Изучите существующую документацию
3. Отправьте подробный отчет об ошибке с:
   - Сообщениями об ошибках
   - Шагами для воспроизведения
   - Информацией о системе
   - Деталями конфигурации

#### Участие в разработке
1. Сделайте форк репозитория
2. Создайте ветки функций
3. Отправьте пул-реквесты с четкими описаниями
4. Следуйте стандартам кодирования в проекте