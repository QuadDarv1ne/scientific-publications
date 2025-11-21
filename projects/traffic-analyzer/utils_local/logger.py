"""
Модуль для настройки логирования в проекте TrafficAnalyzer.
Предоставляет централизованную конфигурацию логгеров для всех компонентов системы.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Настраивает и возвращает логгер с заданными параметрами.

    Args:
        name: Имя логгера (обычно __name__ модуля)
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу для записи логов (опционально)
        format_string: Кастомный формат сообщений (опционально)

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    
    # Если логгер уже настроен, возвращаем его
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Формат по умолчанию
    if format_string is None:
        format_string = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d] - %(message)s'
        )
    
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Консольный вывод
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый вывод (если указан)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_camera_logger(camera_id: int, level: int = logging.INFO) -> logging.Logger:
    """
    Создает специализированный логгер для камеры.

    Args:
        camera_id: Идентификатор камеры
        level: Уровень логирования

    Returns:
        logging.Logger: Логгер для конкретной камеры
    """
    logger_name = f"camera_{camera_id}"
    log_file = f"logs/camera_{camera_id}.log"
    
    return setup_logger(
        name=logger_name,
        level=level,
        log_file=log_file
    )


def get_process_logger(process_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Создает логгер для конкретного процесса обработки.

    Args:
        process_name: Имя процесса
        level: Уровень логирования

    Returns:
        logging.Logger: Логгер для процесса
    """
    return setup_logger(
        name=f"process.{process_name}",
        level=level
    )


class LoggerMixin:
    """
    Миксин для добавления логгера в классы.
    Автоматически создает логгер на основе имени класса.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Возвращает логгер для класса."""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger
