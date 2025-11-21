.PHONY: help build up down restart logs logs-follow status clean clean-all health ps shell-camera1 shell-camera2

# Переменные
PROJECT_NAME = traffic_analyzer
COMPOSE_FILE = docker-compose.yaml

# Помощь - список доступных команд
help:
	@echo "TrafficAnalyzer - Makefile команды:"
	@echo ""
	@echo "  make build          - Собрать Docker образы"
	@echo "  make up             - Запустить все сервисы"
	@echo "  make down           - Остановить все сервисы"
	@echo "  make restart        - Перезапустить все сервисы"
	@echo "  make logs           - Показать логи всех сервисов"
	@echo "  make logs-follow    - Следить за логами в реальном времени"
	@echo "  make logs-camera1   - Показать логи камеры 1"
	@echo "  make logs-camera2   - Показать логи камеры 2"
	@echo "  make status         - Показать статус сервисов"
	@echo "  make health         - Проверить здоровье контейнеров"
	@echo "  make ps             - Показать запущенные контейнеры"
	@echo "  make shell-camera1  - Войти в shell контейнера камеры 1"
	@echo "  make shell-camera2  - Войти в shell контейнера камеры 2"
	@echo "  make clean          - Остановить и удалить контейнеры"
	@echo "  make clean-all      - Удалить контейнеры, образы и volumes"
	@echo "  make setup-env      - Создать .env файл из примера"
	@echo ""
	@echo "Дашборды и UI:"
	@echo "  make open-grafana   - Открыть Grafana в браузере"
	@echo "  make open-kafka-ui  - Открыть Kafka UI в браузере"
	@echo ""

# Сборка образов
build:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) build

# Запуск всех сервисов
up:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) up -d --build

# Остановка всех сервисов
down:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) down

# Перезапуск всех сервисов
restart: down up

# Логи всех сервисов
logs:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs

# Следить за логами
logs-follow:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs -f

# Логи камеры 1
logs-camera1:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs -f traffic_analyzer_camera_1

# Логи камеры 2
logs-camera2:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs -f traffic_analyzer_camera_2

# Логи Kafka
logs-kafka:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs -f kafka

# Логи InfluxDB
logs-influx:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs -f influxdb

# Логи Grafana
logs-grafana:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) logs -f grafana

# Статус сервисов
status:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) ps

# Показать запущенные контейнеры
ps:
	docker ps --filter "name=$(PROJECT_NAME)"

# Проверка здоровья контейнеров
health:
	@echo "Проверка здоровья контейнеров..."
	@docker ps --filter "name=$(PROJECT_NAME)" --format "table {{.Names}}\t{{.Status}}"

# Shell в контейнере камеры 1
shell-camera1:
	docker exec -it traffic_analyzer_camera_1 /bin/bash

# Shell в контейнере камеры 2
shell-camera2:
	docker exec -it traffic_analyzer_camera_2 /bin/bash

# Очистка - остановка и удаление контейнеров
clean:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) down -v

# Полная очистка - удаление контейнеров, образов и volumes
clean-all:
	docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) down -v --rmi all
	@echo "Удаление данных InfluxDB, Grafana и логов..."
	rm -rf services/influxdb_data/* services/grafana/* logs/*

# Создать .env файл из примера
setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env файл создан из .env.example"; \
		echo "Отредактируйте .env файл перед запуском проекта"; \
	else \
		echo ".env файл уже существует"; \
	fi

# Открыть Grafana в браузере
open-grafana:
	@echo "Открытие Grafana (http://localhost:3111)"
	@python -m webbrowser http://localhost:3111

# Открыть Kafka UI в браузере
open-kafka-ui:
	@echo "Открытие Kafka UI (http://localhost:9001)"
	@python -m webbrowser http://localhost:9001

# Быстрый старт проекта
quickstart: setup-env up
	@echo ""
	@echo "✓ TrafficAnalyzer запущен!"
	@echo ""
	@echo "Сервисы доступны по адресам:"
	@echo "  - Grafana:  http://localhost:3111 (admin/admin)"
	@echo "  - Kafka UI: http://localhost:9001"
	@echo "  - Video:    http://localhost:8009"
	@echo ""
	@echo "Для просмотра логов: make logs-follow"
	@echo "Для остановки: make down"
	@echo ""

# Мониторинг в реальном времени
monitor:
	@while true; do \
		clear; \
		echo "=== TrafficAnalyzer Status ==="; \
		echo ""; \
		docker ps --filter "name=$(PROJECT_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"; \
		echo ""; \
		echo "Обновление каждые 5 секунд (Ctrl+C для выхода)..."; \
		sleep 5; \
	done
