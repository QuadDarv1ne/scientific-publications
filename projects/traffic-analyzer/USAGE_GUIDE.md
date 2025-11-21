# 🚀 Руководство по использованию улучшенного TrafficAnalyzer

## Быстрый старт

### 1. Подготовка окружения

```bash
# Клонировать репозиторий
git clone https://github.com/Koldim2001/TrafficAnalyzer.git
cd TrafficAnalyzer

# Создать .env файл из примера
make setup-env
```

Отредактируйте `.env` файл, указав необходимые параметры.

### 2. Запуск проекта

```bash
# Быстрый старт (создание .env + запуск)
make quickstart

# Или поэтапно:
make build    # Собрать образы
make up       # Запустить все сервисы
```

### 3. Проверка состояния

```bash
# Проверить здоровье всех контейнеров
make health

# Показать статус сервисов
make status

# Real-time мониторинг
make monitor
```

## 📊 Доступ к сервисам

После запуска проекта доступны следующие интерфейсы:

- **Grafana**: http://localhost:3111 (admin/admin)
- **Kafka UI**: http://localhost:9001
- **Video Stream**: http://localhost:8009

```bash
# Открыть Grafana в браузере
make open-grafana

# Открыть Kafka UI
make open-kafka-ui
```

## 📝 Работа с логами

```bash
# Все логи
make logs

# Следить за логами в реальном времени
make logs-follow

# Логи конкретных сервисов
make logs-camera1
make logs-camera2
make logs-kafka
make logs-influx
make logs-grafana
```

## 🔧 Управление контейнерами

```bash
# Войти в shell контейнера
make shell-camera1
make shell-camera2

# Перезапустить все сервисы
make restart

# Остановить все сервисы
make down
```

## 🧹 Очистка

```bash
# Остановить и удалить контейнеры
make clean

# Полная очистка (включая данные и образы)
make clean-all
```

## 📈 Мониторинг производительности

Система автоматически собирает и отправляет метрики:

### Метрики в Kafka

Топики:
- `statistics_{N}` - статистика трафика
- `metrics_{N}` - метрики производительности

### Доступные метрики:

**FPS**
- `current_fps` - текущий FPS
- `avg_fps` - средний FPS за окно наблюдения

**Задержки (ms)**
- `detection_latency_ms` - задержка детекции
- `tracking_latency_ms` - задержка трекинга
- `total_latency_ms` - общая задержка

**Очереди**
- `queue_detection_size` - размер очереди детекции
- `queue_tracking_size` - размер очереди трекинга

**Объекты**
- `objects_detected` - обнаруженные объекты
- `active_tracks` - активные треки

## 🔍 Логирование

### Уровни логирования

Логи разделены по процессам:
- `main` - главный процесс
- `frame_reader_detection` - чтение и детекция
- `tracker_update_calc` - трекинг и статистика
- `show_node` - отображение

### Просмотр логов

Логи хранятся в директории `logs/`:
```
logs/
├── camera_1.log
├── camera_2.log
└── ...
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# InfluxDB
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=admin

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# Kafka
KAFKA_USERNAME=traffic
KAFKA_PASSWORD=traffic-secret

# Камера 1
CAMERA_1_VIDEO_SRC=test_videos/test_video.mp4
CAMERA_1_ROADS_JSON=configs/entry_exit_lanes.json
CAMERA_1_TOPIC_NAME=statistics_1
CAMERA_1_ID=1
```

### Конфигурация приложения

Основная конфигурация в `configs/app_config.yaml`:

```yaml
pipeline:
  save_video: False
  show_in_web: True
  send_info_kafka: True

detection_node:
  weight_pth: weights/yolov8m.pt
  confidence: 0.10
  # ...
```

## 🐛 Отладка

### Проверка healthcheck

```bash
# Статус всех контейнеров
docker ps

# Логи healthcheck конкретного контейнера
docker inspect traffic_analyzer_camera_1
```

### Отладка в контейнере

```bash
# Войти в контейнер
make shell-camera1

# Внутри контейнера:
python healthcheck.py  # Проверка здоровья
ls -la logs/           # Просмотр логов
```

### Отладка Kafka

```bash
# Открыть Kafka UI
make open-kafka-ui

# Или через логи
make logs-kafka
```

## 📚 Дополнительная информация

### Добавление новой камеры

1. Добавьте переменные в `.env`:
```env
CAMERA_3_VIDEO_SRC=rtsp://192.168.1.103:554/stream
CAMERA_3_ROADS_JSON=configs/entry_exit_lanes_cam3.json
CAMERA_3_TOPIC_NAME=statistics_3
CAMERA_3_ID=3
```

2. Добавьте сервис в `docker-compose.yaml`:
```yaml
traffic_analyzer_camera_3:
  image: traffic_analyzer:latest
  # ... скопируйте конфигурацию camera_1/2 и измените ID
```

3. Перезапустите проект:
```bash
make restart
```

### Локальный запуск без Docker

```bash
# Установка зависимостей
python -m pip install --upgrade pip
pip install "numpy<2"
pip install cython_bbox==0.1.5 lap==0.4.0
pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Запуск
python main_optimized.py pipeline.send_info_kafka=False
```

## 🆘 Решение проблем

### Контейнер не запускается

```bash
# Проверить логи
make logs-camera1

# Пересобрать образ
make build
make up
```

### Ошибки подключения к Kafka

```bash
# Проверить статус Kafka
make logs-kafka

# Проверить healthcheck
make health
```

### Нет видео в веб-интерфейсе

1. Проверьте логи Flask сервера
2. Убедитесь что `show_in_web: True` в конфиге
3. Проверьте порт 8009

## 📞 Поддержка

- GitHub: https://github.com/Koldim2001/TrafficAnalyzer
- Issues: https://github.com/Koldim2001/TrafficAnalyzer/issues

## 📖 Документация

- `README.md` - общее описание проекта
- `IMPROVEMENTS.md` - список улучшений
- `USAGE_GUIDE.md` - это руководство
