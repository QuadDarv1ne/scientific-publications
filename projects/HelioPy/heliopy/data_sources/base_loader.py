"""
Base class for data loaders.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import requests
from tqdm import tqdm


class BaseLoader(ABC):
    """Base class for all data loaders."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the loader.

        Parameters
        ----------
        cache_dir : Path, optional
            Directory for caching data.
        """
        from heliopy.utils.config import get_config

        config = get_config()
        self.cache_dir = cache_dir or config.cache_dir / self.__class__.__name__.lower()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = config

    @abstractmethod
    def load(self, *args, **kwargs):
        """Abstract method for loading data."""
        pass

    def _download_file(self, url: str, filepath: Path, timeout: Optional[int] = None) -> Path:
        """
        Download a file by URL.

        Parameters
        ----------
        url : str
            File URL.
        filepath : Path
            Path to save the file.
        timeout : int, optional
            Download timeout in seconds.

        Returns
        -------
        Path
            Path to the downloaded file.
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
        Get the path to a cached file.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        Path or None
            Path to the file if it exists.
        """
        filepath = self.cache_dir / filename
        if filepath.exists():
            return filepath
        return None
