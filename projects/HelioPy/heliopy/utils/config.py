"""
HelioPy library configuration.
"""

import os
from pathlib import Path
from typing import Optional, Union

import yaml


class Config:
    """Class for managing library configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration.

        Parameters
        ----------
        config_path : str, optional
            Path to the configuration file. If not specified, the default configuration is used.
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
        """Load default configuration."""
        self.cache_enabled = True
        self.cache_size_limit_gb = 10
        self.download_timeout = 300
        self.max_workers = 4
        self.verbose = False

    def _load_from_file(self, config_path: str):
        """Load configuration from file."""
        with open(config_path) as f:
            config = yaml.safe_load(f)
            for key, value in config.items():
                setattr(self, key, value)

    @property
    def cache_dir(self) -> Path:
        """Path to the cache directory."""
        return self._cache_dir

    @property
    def data_dir(self) -> Path:
        """Path to the data directory."""
        return self._data_dir

    @property
    def config_dir(self) -> Path:
        """Path to the configuration directory."""
        return self._config_dir

    def save(self, config_path: Optional[Union[str, Path]] = None):
        """Save configuration to file."""
        if config_path is None:
            config_path = self._config_dir / "config.yaml"

        config_dict = {
            "cache_enabled": self.cache_enabled,
            "cache_size_limit_gb": self.cache_size_limit_gb,
            "download_timeout": self.download_timeout,
            "max_workers": self.max_workers,
            "verbose": self.verbose,
        }

        with open(config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)


# Глобальный экземпляр конфигурации
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set the global configuration instance."""
    global _config
    _config = config
