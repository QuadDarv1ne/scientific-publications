# Docker Quick Start Guide

## 🚀 Быстрый старт с Docker Compose

### Базовая установка (только мониторинг)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/QuadDarv1ne/starlink_performance_monitor.git
cd starlink_performance_monitor

# 2. Создайте конфигурацию
cp config.example.json config.json
# Отредактируйте config.json под свои нужды

# 3. Запустите контейнеры
docker-compose up -d

# 4. Проверьте статус
docker-compose ps

# 5. Просмотрите логи
docker-compose logs -f app
```

### Полная установка (с Prometheus и Grafana)

```bash
# Запуск всех сервисов включая monitoring стек
docker-compose --profile monitoring up -d

# Проверка всех сервисов
docker-compose --profile monitoring ps
```

## 📊 Доступные сервисы

После запуска доступны следующие сервисы:

| Сервис | URL | Описание |
|--------|-----|----------|
| Web Dashboard | http://localhost:8050 | Основной веб-интерфейс |
| Prometheus Exporter | http://localhost:9817/metrics | Метрики в формате Prometheus |
| Prometheus UI | http://localhost:9090 | Prometheus (только с `--profile monitoring`) |
| Grafana | http://localhost:3000 | Grafana dashboards (только с `--profile monitoring`) |
| PostgreSQL | localhost:5432 | База данных (внутренний доступ) |

**Grafana credentials:**
- Username: `admin`
- Password: `admin`

## 🔧 Управление контейнерами

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (ВНИМАНИЕ: удаляет все данные!)
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart app

# Просмотр логов
docker-compose logs -f app        # Мониторинг
docker-compose logs -f exporter   # Prometheus exporter
docker-compose logs -f web        # Web dashboard

# Выполнение команд внутри контейнера
docker-compose exec app python -m pytest tests/
docker-compose exec db psql -U starlink_user -d starlink_monitor
```

## 📦 Сервисы в Docker Compose

### app (Монитор производительности)
- Собирает метрики каждые 15 минут
- Сохраняет в PostgreSQL
- Интегрируется с метеоданными

### exporter (Prometheus Exporter)
- Экспортирует метрики на порту 9817
- Обновляется каждые 3 секунды
- Совместим с Grafana

### web (Веб-дашборд)
- Интерактивные графики
- История метрик
- Генерация отчетов

### db (PostgreSQL)
- Хранение всех метрик
- Автоматический бэкап (через volumes)

### prometheus (опционально)
- Сбор метрик из exporter
- Хранение time-series данных
- Query API для Grafana

### grafana (опционально)
- Визуализация метрик
- Готовые дашборды
- Алерты и уведомления

## 🔐 Безопасность

### Рекомендации для production:

1. **Смените пароли в docker-compose.yml:**
```yaml
environment:
  POSTGRES_PASSWORD: your_secure_password  # Измените!
  GF_SECURITY_ADMIN_PASSWORD: grafana_password  # Измените!
```

2. **Используйте secrets для чувствительных данных:**
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

3. **Ограничьте доступ к портам:**
```yaml
ports:
  - "127.0.0.1:5432:5432"  # Только localhost
```

4. **Включите SSL для PostgreSQL**

## 📈 Настройка Grafana

1. Откройте http://localhost:3000
2. Войдите (admin/admin)
3. Добавьте Prometheus data source:
   - URL: `http://prometheus:9090`
   - Access: `Server (default)`
4. Импортируйте дашборд:
   - ID: 14337 (Starlink dashboard)
   - Или создайте свой с метриками из `exporter:9817/metrics`

## 🛠️ Troubleshooting

### Проблема: База данных не запускается
```bash
# Проверьте логи
docker-compose logs db

# Убедитесь что порт 5432 свободен
netstat -an | grep 5432

# Пересоздайте volume
docker-compose down -v
docker-compose up -d
```

### Проблема: Exporter не отдаёт метрики
```bash
# Проверьте что база доступна
docker-compose exec exporter ping db

# Проверьте логи exporter
docker-compose logs exporter

# Вручную проверьте метрики
curl http://localhost:9817/metrics
```

### Проблема: Недостаточно места для данных
```bash
# Проверьте размер volumes
docker system df

# Очистите старые данные
docker volume prune

# Или настройте retention policy в Prometheus
```

## 📚 Дополнительные команды

```bash
# Обновление образов
docker-compose pull
docker-compose up -d --build

# Бэкап базы данных
docker-compose exec db pg_dump -U starlink_user starlink_monitor > backup.sql

# Восстановление из бэкапа
cat backup.sql | docker-compose exec -T db psql -U starlink_user starlink_monitor

# Просмотр использования ресурсов
docker stats

# Масштабирование (например, запуск 3 workers)
docker-compose up -d --scale app=3
```

## 🌐 Интеграция с облачными сервисами

### Grafana Cloud
```yaml
# Добавьте remote_write в prometheus.yml
remote_write:
  - url: https://prometheus-prod-XX-prod-XX.grafana.net/api/prom/push
    basic_auth:
      username: YOUR_USERNAME
      password: YOUR_API_KEY
```

### Docker Swarm / Kubernetes
См. документацию по развёртыванию в production окружениях.

---

**Готово!** Система мониторинга Starlink запущена и готова к работе 🚀

Для получения помощи см. [README.md](README.md) или создайте [issue](https://github.com/QuadDarv1ne/starlink_performance_monitor/issues).
