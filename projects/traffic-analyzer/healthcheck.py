#!/usr/bin/env python3
"""
Скрипт для проверки здоровья контейнера traffic_analyzer.
Используется в Docker healthcheck для мониторинга состояния приложения.
"""

import sys
import os
from pathlib import Path


def check_health() -> bool:
    """
    Проверяет состояние приложения.
    
    Returns:
        bool: True если приложение работает нормально, иначе False
    """
    try:
        # Проверка существования лог-файлов (если логирование настроено)
        logs_dir = Path("/app/logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if not log_files:
                return False
        
        # Можно добавить дополнительные проверки:
        # - Проверка доступности Flask сервера
        # - Проверка подключения к Kafka
        # - Проверка очередей multiprocessing
        
        return True
    
    except Exception as e:
        print(f"Health check failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    is_healthy = check_health()
    sys.exit(0 if is_healthy else 1)
