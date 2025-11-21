#!/usr/bin/env python3
"""
Скрипт для проверки здоровья контейнера traffic_analyzer.
Используется в Docker healthcheck для мониторинга состояния приложения.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import socket


def check_log_files() -> tuple[bool, str]:
    """
    Проверяет существование и актуальность лог-файлов.
    
    Returns:
        tuple[bool, str]: (статус проверки, сообщение об ошибке)
    """
    try:
        logs_dir = Path("/app/logs")
        if not logs_dir.exists():
            return False, "Директория логов не существует"
        
        log_files = list(logs_dir.glob("*.log"))
        if not log_files:
            return False, "Лог-файлы не найдены"
        
        # Проверка, что логи обновлялись недавно (в течение последних 5 минут)
        for log_file in log_files:
            if log_file.stat().st_size > 0:
                modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if datetime.now() - modified_time < timedelta(minutes=5):
                    return True, "OK"
        
        return False, "Лог-файлы не обновлялись более 5 минут"
    
    except Exception as e:
        return False, f"Ошибка проверки логов: {e}"


def check_flask_server() -> tuple[bool, str]:
    """
    Проверяет доступность Flask сервера.
    
    Returns:
        tuple[bool, str]: (статус проверки, сообщение об ошибке)
    """
    try:
        port = int(os.environ.get('FLASK_PORT', 8100))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            return True, "OK"
        else:
            return False, f"Flask сервер недоступен на порту {port}"
    
    except Exception as e:
        return False, f"Ошибка проверки Flask: {e}"


def check_weights_file() -> tuple[bool, str]:
    """
    Проверяет наличие весов модели YOLO.
    
    Returns:
        tuple[bool, str]: (статус проверки, сообщение об ошибке)
    """
    try:
        weights_path = Path("/app/weights/yolov8m.pt")
        if weights_path.exists():
            return True, "OK"
        else:
            return False, "Файл весов модели не найден"
    
    except Exception as e:
        return False, f"Ошибка проверки весов: {e}"


def check_config_file() -> tuple[bool, str]:
    """
    Проверяет наличие конфигурационного файла.
    
    Returns:
        tuple[bool, str]: (статус проверки, сообщение об ошибке)
    """
    try:
        config_path = Path("/app/configs/app_config.yaml")
        if config_path.exists():
            return True, "OK"
        else:
            return False, "Конфигурационный файл не найден"
    
    except Exception as e:
        return False, f"Ошибка проверки конфига: {e}"


def check_health() -> bool:
    """
    Проверяет состояние приложения.
    
    Returns:
        bool: True если приложение работает нормально, иначе False
    """
    checks = [
        ("Конфигурация", check_config_file),
        ("Веса модели", check_weights_file),
        ("Логи", check_log_files),
        ("Flask сервер", check_flask_server),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        passed, message = check_func()
        if not passed:
            print(f"❌ {check_name}: {message}", file=sys.stderr)
            all_passed = False
        else:
            print(f"✓ {check_name}: {message}")
    
    return all_passed


if __name__ == "__main__":
    is_healthy = check_health()
    sys.exit(0 if is_healthy else 1)
