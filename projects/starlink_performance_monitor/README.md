## 📄 README.md для Starlink Performance Monitor

```markdown
# 📊 Starlink Performance Monitor

![Performance Dashboard](https://via.placeholder.com/800x400?text=Starlink+Performance+Dashboard) <!-- Замените на реальный скриншот -->

**Automated performance monitoring and analysis tool for Starlink satellite internet**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/yourusername/starlink-monitor/ci.yml?branch=main)](https://github.com/yourusername/starlink-monitor/actions)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://hub.docker.com/r/yourusername/starlink-monitor)

## 📖 Описание

Starlink Performance Monitor — это комплексное решение для автоматического мониторинга качества интернет-соединения через Starlink. Проект собирает, анализирует и визуализирует ключевые метрики производительности (скорость загрузки/выгрузки, пинг, потеря пакетов) с возможностью сравнения с другими провайдерами и прогнозирования аномалий.

**Ключевые возможности:**
- 📈 Автоматический сбор метрик производительности каждые 5-60 минут
- 📊 Интерактивные дашборды с графиками и тепловыми картами
- 🔍 Сравнение производительности Starlink с другими интернет-провайдерами
- ⚠️ Обнаружение аномалий и автоматические оповещения
- 🌤️ Корреляция производительности с метеоданными
- 📱 Мобильные уведомления через Telegram/Email
- 📤 Экспорт отчетов в PDF/CSV/Excel

## 🚀 Особенности

### 📊 Автоматический сбор данных
- **Speedtest**: Измерение скорости через speedtest-cli и собственные серверы
- **Ping Tests**: Проверка задержки до ключевых точек (Google DNS, Cloudflare, локальные серверы)
- **Packet Loss**: Тестирование потери пакетов с использованием ICMP и UDP
- **DNS Resolution**: Замер времени разрешения DNS-имен
- **HTTP Latency**: Тестирование времени отклика веб-серверов

### 📈 Продвинутый анализ
- **Часовые паттерны**: Анализ производительности по времени суток
- **Сезонные тренды**: Выявление сезонных закономерностей
- **Аномалии**: Автоматическое обнаружение отклонений от нормы
- **Сравнение**: Сравнение с наземными провайдерами и мобильным интернетом
- **Прогнозирование**: ML-модели для прогнозирования производительности

### 🔔 Система оповещений
- **Threshold-based alerts**: Уведомления при падении скорости ниже порога
- **Anomaly detection**: Предупреждения о необычной активности
- **Scheduled reports**: Ежедневные/еженедельные отчеты
- **Multiple channels**: Telegram, Email, Push-уведомления
- **Escalation policies**: Многоуровневые оповещения для критических ситуаций

### 🌐 Веб-интерфейс
- **Real-time dashboard**: Живые графики производительности
- **Historical data**: Просмотр архивных данных за любой период
- **Custom views**: Настройка виджетов и метрик
- **Multi-location**: Поддержка нескольких точек мониторинга
- **User management**: Роли и права доступа для командной работы

## ⚙️ Требования

### Системные требования
- Python 3.8 или новее
- 1 ГБ оперативной памяти
- 10 ГБ свободного места на диске (для хранения истории)
- Подключение к интернету
- (Опционально) Доступ к другим интернет-провайдерам для сравнения

### Зависимости Python
```python
speedtest-cli==2.3.0
ping3==4.0.4
pandas==2.0.1
numpy==1.24.3
matplotlib==3.7.1
plotly==5.15.0
dash==2.11.1
sqlalchemy==2.0.15
psycopg2-binary==3.1.8  # Для PostgreSQL
requests==2.29.0
schedule==1.2.0
python-telegram-bot==20.4
scikit-learn==1.3.0
statsmodels==0.14.0
openmeteo_requests==1.0.0  # Для метеоданных
flask==2.3.2
pytest==7.4.0
pytest-cov==4.1.0
pylint==2.17.4
black==23.3.0
sphinx==7.0.1
sphinx-rtd-theme==1.2.2
```

## 📦 Установка

Вариант 1: Локальная установка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/starlink-monitor.git
cd starlink-monitor

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Проверка установки
python test_installation.py

# Настройка базы данных
python setup_database.py

# Копирование конфигурации
cp config.example.json config.json
```

Вариант 2: Docker (рекомендуется)

```bash
# Сборка и запуск контейнеров
docker-compose up -d --build

# Инициализация базы данных
docker-compose exec app python setup_database.py
```

Вариант 3: Установка как сервис (Linux)

```bash
# Копирование сервисного файла
sudo cp starlink-monitor.service /etc/systemd/system/

# Настройка прав
sudo chown root:root /etc/systemd/system/starlink-monitor.service
sudo chmod 644 /etc/systemd/system/starlink-monitor.service

# Создание пользователя
sudo useradd --system --no-create-home starlink

# Создание директории и копирование файлов
sudo mkdir -p /opt/starlink-monitor
sudo cp -r . /opt/starlink-monitor/
sudo chown -R starlink:starlink /opt/starlink-monitor

# Создание виртуального окружения
sudo -u starlink python3 -m venv /opt/starlink-monitor/venv
sudo -u starlink /opt/starlink-monitor/venv/bin/pip install -r /opt/starlink-monitor/requirements.txt

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable starlink-monitor
sudo systemctl start starlink-monitor
```

## ⚙️ Конфигурация

Создайте файл config.json:
```json
{
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "name": "starlink_monitor",
    "user": "monitor_user",
    "password": "secure_password"
  },
  "monitoring": {
    "starlink": {
      "enabled": true,
      "interval_minutes": 15,
      "servers": [
        {
          "name": "Google DNS",
          "host": "8.8.8.8",
          "port": 53
        },
        {
          "name": "Cloudflare",
          "host": "1.1.1.1",
          "port": 53
        }
      ],
      "speedtest": {
        "enabled": true,
        "servers": [23456, 12345],  # ID серверов speedtest
        "threads": 4
      }
    },
    "comparison_providers": [
      {
        "name": "Local ISP",
        "interface": "eth0",
        "enabled": false
      },
      {
        "name": "Mobile 4G",
        "interface": "wwan0",
        "enabled": false
      }
    ]
  },
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_telegram_bot_token",
      "chat_id": "your_chat_id",
      "thresholds": {
        "download_mbps": 50,
        "upload_mbps": 10,
        "ping_ms": 100,
        "packet_loss_percent": 5
      }
    },
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "port": 587,
      "username": "your.email@gmail.com",
      "password": "your_app_password",
      "recipients": ["admin@example.com"],
      "daily_report_hour": 8
    }
  },
  "weather": {
    "enabled": true,
    "api_key": "openmeteo_api_key",
    "location": {
      "latitude": 55.7558,
      "longitude": 37.6173
    },
    "parameters": ["temperature_2m", "precipitation", "wind_speed_10m", "cloud_cover"]
  },
  "web": {
    "host": "0.0.0.0",
    "port": 8050,
    "debug": false,
    "auth": {
      "enabled": true,
      "users": [
        {
          "username": "admin",
          "password_hash": "hashed_password_here",
          "role": "admin"
        }
      ]
    }
  }
}
```

## 🚦 Использование

Запуск основного мониторинга

```bash
python monitor.py --config config.json
```

Запуск веб-интерфейса

```bash
python web_app.py --port 8050
```

Генерация отчетов

```bash
# Ежедневный отчет
python generate_report.py --type daily --output daily_report.pdf

# Недельный отчет
python generate_report.py --type weekly --output weekly_report.pdf

# Пользовательский период
python generate_report.py --start "2025-11-01" --end "2025-11-07" --format excel
```

Ручное тестирование

```bash
# Запуск одного цикла тестов
python manual_test.py

# Тест только скорости
python manual_test.py --type speed

# Тест только пинга
python manual_test.py --type ping
```

Команды Docker

```bash
# Просмотр логов
docker-compose logs -f app

# Запуск тестов в контейнере
docker-compose exec app python manual_test.py

# Бэкап базы данных
docker-compose exec db pg_dump -U monitor_user starlink_monitor > backup.sql
```

## 🧪 Тестирование

Запуск unit-тестов

```bash
python -m pytest test_monitor.py -v
```

Проверка установки

```bash
python test_installation.py
```

## 📊 Веб-интерфейс

После запуска веб-приложения откройте http://localhost:8050 в браузере.

Доступные страницы:
Dashboard - Главная страница с текущими метриками
Performance - Исторические данные и графики
Comparison - Сравнение с другими провайдерами
Alerts - История оповещений и настройки
Reports - Генерация и просмотр отчетов
Settings - Настройки системы и пользователей

Особенности дашборда:
📈 Live Metrics: Реальные значения скорости и пинга
🌡️ Weather Correlation: Связь погоды и производительности
📊 Heat Maps: Тепловые карты по времени суток
📉 Trend Analysis: Долгосрочные тренды и прогнозы
⚠️ Alert Panel: Текущие предупреждения и инциденты

## 🔧 Расширенная настройка

Интеграция с Grafana

```yaml
# docker-compose.override.yml
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./grafana_data:/var/lib/grafana
    depends_on:
      - db
```

Настройка cron для автоматических отчетов

```bash
# Ежедневный отчет в 8 утра
0 8 * * * /path/to/venv/bin/python /path/to/generate_report.py --type daily --email admin@example.com

# Еженедельный отчет по понедельникам
0 9 * * 1 /path/to/venv/bin/python /path/to/generate_report.py --type weekly --format pdf --output /reports/weekly_$(date +\%Y-\%m-\%d).pdf
```

Настройка reverse proxy (Nginx)

```nginx
server {
    listen 80;
    server_name monitor.yourdomain.com;

    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🤝 Вклад в проект

Мы активно принимаем вклады! См. CONTRIBUTING.md для инструкций.

Приоритетные задачи:
📱 Мобильное приложение для мониторинга
🤖 Продвинутые ML-модели для прогнозирования
🌍 Глобальная сеть мониторинга с crowdsourcing
📡 Интеграция с оборудованием Starlink (Dishy API)
📊 Расширенные отчеты для бизнес-аналитики

## 📜 Лицензия

Проект распространяется под лицензией Apache License 2.0. См. LICENSE для подробностей.

## 🙏 Благодарности

Speedtest.net - Инфраструктура для тестирования скорости
Open-Meteo - Бесплатные метеоданные
Plotly/Dash - Фреймворк для веб-визуализации
PostgreSQL - Надежная база данных
SpaceX и сообщество Starlink за вдохновение

## 📬 Поддержка

Для вопросов и поддержки, пожалуйста:

Создайте issue в GitHub
Напишите в Telegram: @starlink_monitor_support
Email: support@starlink-monitor.example.com
```