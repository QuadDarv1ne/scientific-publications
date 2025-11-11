"""
Базовый класс для загрузчиков данных.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import requests
from tqdm import tqdm


class BaseLoader(ABC):
    """Базовый класс для всех загрузчиков данных."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Инициализация загрузчика.

        Parameters
        ----------
        cache_dir : Path, optional
            Директория для кэширования данных.
        """
        from heliopy.utils.config import get_config

        config = get_config()
        self.cache_dir = cache_dir or config.cache_dir / self.__class__.__name__.lower()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = config

    @abstractmethod
    def load(self, *args, **kwargs):
        """Абстрактный метод загрузки данных."""
        pass

    def _download_file(self, url: str, filepath: Path, timeout: Optional[int] = None) -> Path:
        """
        Загрузка файла по URL.

        Parameters
        ----------
        url : str
            URL файла.
        filepath : Path
            Путь для сохранения файла.
        timeout : int, optional
            Таймаут загрузки в секундах.

        Returns
        -------
        Path
            Путь к загруженному файлу.
        """
        if filepath.exists():
            return filepath

        timeout = timeout or self.config.download_timeout

        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(filepath, "wb") as f, tqdm(
            desc=filepath.name,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        return filepath

    def _get_cached_file(self, filename: str) -> Optional[Path]:
        """
        Получение пути к закэшированному файлу.

        Parameters
        ----------
        filename : str
            Имя файла.

        Returns
        -------
        Path или None
            Путь к файлу, если он существует.
        """
        filepath = self.cache_dir / filename
        if filepath.exists():
            return filepath
        return None
