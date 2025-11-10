"""
Конфигурация библиотеки HelioPy.
"""

import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Класс для управления конфигурацией библиотеки."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация конфигурации.
        
        Parameters
        ----------
        config_path : str, optional
            Путь к файлу конфигурации. Если не указан, используется конфигурация по умолчанию.
        """
        self._cache_dir = Path.home() / ".heliopy" / "cache"
        self._data_dir = Path.home() / ".heliopy" / "data"
        self._config_dir = Path.home() / ".heliopy" / "config"
        
        # Создание директорий при необходимости
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        # Загрузка конфигурации из файла, если указан
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
        else:
            self._load_defaults()
    
    def _load_defaults(self):
        """Загрузка конфигурации по умолчанию."""
        self.cache_enabled = True
        self.cache_size_limit_gb = 10
        self.download_timeout = 300
        self.max_workers = 4
        self.verbose = False
    
    def _load_from_file(self, config_path: str):
        """Загрузка конфигурации из файла."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            for key, value in config.items():
                setattr(self, key, value)
    
    @property
    def cache_dir(self) -> Path:
        """Путь к директории кэша."""
        return self._cache_dir
    
    @property
    def data_dir(self) -> Path:
        """Путь к директории данных."""
        return self._data_dir
    
    @property
    def config_dir(self) -> Path:
        """Путь к директории конфигурации."""
        return self._config_dir
    
    def save(self, config_path: Optional[str] = None):
        """Сохранение конфигурации в файл."""
        if config_path is None:
            config_path = self._config_dir / "config.yaml"
        
        config_dict = {
            'cache_enabled': self.cache_enabled,
            'cache_size_limit_gb': self.cache_size_limit_gb,
            'download_timeout': self.download_timeout,
            'max_workers': self.max_workers,
            'verbose': self.verbose,
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)


# Глобальный экземпляр конфигурации
_config = None


def get_config() -> Config:
    """Получить глобальный экземпляр конфигурации."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Установить глобальный экземпляр конфигурации."""
    global _config
    _config = config

