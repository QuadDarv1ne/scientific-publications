# 🛰️ Starlink Satellite Tracker & Visualizer

![Starlink Tracker Preview](https://via.placeholder.com/800x400?text=Starlink+Tracker+Preview) <!-- Замените на реальный скриншот -->

**Real-time satellite tracking and visualization system for SpaceX Starlink constellation**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/starlink-tracker?style=social)](https://github.com/yourusername/starlink-tracker)

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Run the tracker
python main.py --help

# Start the web interface
python web_app.py
```

## 📖 Описание

Starlink Satellite Tracker & Visualizer — это Python-приложение для отслеживания спутников Starlink в реальном времени с возможностью 3D-визуализации их орбит и прогнозирования прохождений над вашим местоположением. Проект использует астрономические вычисления для точного расчета позиций спутников и предоставляет интерактивные визуализации для лучшего понимания космического созвездия.

**Основные возможности:**
- 📡 Автоматическая загрузка актуальных TLE (Two-Line Elements) данных с Celestrak
- 🌍 Точное расчет позиций спутников с использованием библиотеки Skyfield
- 🗺️ Интерактивная 3D-визуализация орбит спутников
- 📍 Прогноз видимости спутников над выбранным местоположением
- 🔔 Уведомления о прохождениях спутников над вашим регионом
- 📊 Экспорт данных в CSV/JSON для дальнейшего анализа
- 🌐 Визуализация покрытия Starlink на карте мира

## 🚀 Особенности

### 📡 Автоматическое обновление данных
- Ежедневная загрузка свежих TLE данных с официальных источников
- Кэширование данных для работы в автономном режиме
- Обработка ошибок при недоступности источников

### 🌍 Расчет видимости
- Определение времени восхода и захода спутников
- Расчет высоты и азимута для оптимального наблюдения
- Фильтрация спутников по минимальной высоте над горизонтом
- Учет местного времени и часовых поясов

### 🎨 Визуализация
- **3D орбиты**: Интерактивная визуализация в matplotlib/plotly
- **Карта покрытия**: Отображение текущих позиций спутников на карте мира
- **Графики высоты**: Визуализация траекторий прохождения над точкой наблюдения
- **Анимация движения**: Динамическое отображение перемещения спутников

### 🔔 Система уведомлений
- Email-уведомления о прохождениях спутников
- Push-уведомления через Telegram бота
- Настройка критериев для уведомлений (минимальная высота, яркость)

## ⚙️ Требования

### Системные требования
- Python 3.8 или новее
- 2 ГБ оперативной памяти
- 500 МБ свободного места на диске
- Подключение к интернету для загрузки TLE данных

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

Установите зависимости с помощью:
```bash
pip install -r requirements.txt
```

### Аргументы командной строки

```
usage: main.py [-h] [--update] [--visualize] [--notify] [--debug]

Starlink Satellite Tracker

optional arguments:
  -h, --help      show this help message and exit
  --update        Force update TLE data
  --visualize     Show 3D visualization (default: False)
  --notify        Send notifications for upcoming passes
  --debug         Enable debug logging
```

### Примеры использования

```bash
# Обновить данные TLE и показать предстоящие прохождения
python main.py --update

# Показать 3D визуализацию орбит
python main.py --visualize

# Включить отладочный режим
python main.py --debug
```

## 🖥️ Веб-интерфейс
При запуске web_app.py доступны следующие страницы:

/ - Главная страница с текущими позициями спутников
/passes - Календарь прохождений над вашим местоположением
/coverage - Карта покрытия Starlink по всему миру
/settings - Настройки наблюдателя и уведомлений
/export - Экспорт данных в различных форматах

### Запуск веб-интерфейса

```bash
python web_app.py
```

После запуска откройте в браузере http://localhost:5000

Отчет по видимости

```
Starlink Passes Report for Moscow Observatory
Generated: 2025-11-10 15:30:00 MSK
Period: Next 24 hours

┌───────────────┬────────────┬────────────┬────────────┬──────────────┐
│ Satellite ID  │ Start Time │ Max Height │ Duration   │ Max Elevation│
├───────────────┼────────────┼────────────┼────────────┼──────────────┤
│ STARLINK-1234 │ 18:45:23   │ 65°        │ 4m 12s     │ 42°          │
│ STARLINK-5678 │ 19:12:08   │ 78°        │ 5m 37s     │ 58°          │
│ STARLINK-9012 │ 20:03:45   │ 45°        │ 3m 21s     │ 28°          │
└───────────────┴────────────┴────────────┴────────────┴──────────────┘
```

🔧 Конфигурация
Файл конфигурации config.json

```
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

📜 Лицензия
Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

🙏 Благодарности
Skyfield - Библиотека для астрономических расчетов
Celestrak - Источник TLE данных
Space-Track.org - Дополнительные данные о спутниках
OpenStreetMap - Данные для карт
SpaceX за создание революционной системы спутниковой связи

