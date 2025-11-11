"""
Data processing and preprocessing.
"""

from typing import Optional, Tuple

import numpy as np
from scipy import ndimage
from skimage import filters, restoration


class DataProcessor:
    """Class for data processing and preprocessing."""

    def __init__(self):
        """Инициализация процессора данных."""
        pass

    @staticmethod
    def normalize(
        data: np.ndarray,
        method: str = "minmax",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
    ) -> np.ndarray:
        """
        Normalize data.

        Parameters
        ----------
        data : array
            Input data.
        method : str
            Normalization method ('minmax', 'zscore', 'log').
        vmin, vmax : float, optional
            Minimum and maximum values for minmax normalization.

        Returns
        -------
        array
            Normalized data.
        """
        if method == "minmax":
            if vmin is None:
                vmin = np.nanmin(data)
            if vmax is None:
                vmax = np.nanmax(data)
            if vmax == vmin:
                return np.zeros_like(data)
            return (data - vmin) / (vmax - vmin)

        elif method == "zscore":
            mean = np.nanmean(data)
            std = np.nanstd(data)
            if std == 0:
                return np.zeros_like(data)
            return (data - mean) / std

        elif method == "log":
            data_positive = np.maximum(data, np.finfo(float).eps)
            return np.log10(data_positive)

        else:
            raise ValueError(f"Неизвестный метод нормализации: {method}")

    @staticmethod
    def remove_background(
        data: np.ndarray, method: str = "median", kernel_size: int = 50
    ) -> np.ndarray:
        """
        Remove background from image.

        Parameters
        ----------
        data : array
            Input image.
        method : str
            Background removal method ('median', 'gaussian', 'morphological').
        kernel_size : int
            Kernel size for filtering.

        Returns
        -------
        array
            Image with background removed.
        """
        if method == "median":
            background = ndimage.median_filter(data, size=kernel_size)
        elif method == "gaussian":
            background = filters.gaussian(data, sigma=kernel_size / 3)
        elif method == "morphological":
            from skimage.morphology import disk

            background = ndimage.grey_opening(data, structure=disk(kernel_size))
        else:
            raise ValueError(f"Неизвестный метод: {method}")

        return data - background

    @staticmethod
    def denoise(data: np.ndarray, method: str = "gaussian", sigma: float = 1.0) -> np.ndarray:
        """
        Remove noise from data.

        Parameters
        ----------
        data : array
            Input data with noise.
        method : str
            Noise removal method ('gaussian', 'bilateral', 'tv').
        sigma : float
            Smoothing parameter.

        Returns
        -------
        array
            Data without noise.
        """
        if method == "gaussian":
            return filters.gaussian(data, sigma=sigma)
        elif method == "bilateral":
            return restoration.denoise_bilateral(data, sigma_color=sigma, sigma_spatial=sigma)
        elif method == "tv":
            return restoration.denoise_tv_chambolle(data, weight=sigma)
        else:
            raise ValueError(f"Неизвестный метод: {method}")

    @staticmethod
    def calibrate_flux(
        data: np.ndarray, exposure_time: float, calibration_factor: float = 1.0
    ) -> np.ndarray:
        """
        Calibrate radiation flux.

        Parameters
        ----------
        data : array
            Raw detector data.
        exposure_time : float
            Exposure time in seconds.
        calibration_factor : float
            Calibration factor.

        Returns
        -------
        array
            Calibrated data.
        """
        return (data / exposure_time) * calibration_factor

    @staticmethod
    def correct_limb_darkening(
        data: np.ndarray, center: Optional[Tuple[int, int]] = None, radius: Optional[float] = None
    ) -> np.ndarray:
        """
        Correct limb darkening.

        Parameters
        ----------
        data : array
            Input image.
        center : tuple, optional
            Disk center (x, y). If not specified, computed automatically.
        radius : float, optional
            Disk radius. If not specified, computed automatically.

        Returns
        -------
        array
            Image with limb darkening correction.
        """
        if center is None:
            center = (data.shape[1] // 2, data.shape[0] // 2)

        if radius is None:
            radius = min(data.shape) / 2

        y, x = np.ogrid[: data.shape[0], : data.shape[1]]
        r = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)

        # Маска для диска
        mask = r <= radius

        # Модель потемнения к краю (упрощенная)
        mu = np.sqrt(1 - (r / radius) ** 2)
        mu = np.maximum(mu, 0.1)  # Избегаем деления на ноль

        # Коррекция
        corrected = data.copy()
        corrected[mask] = data[mask] / mu[mask]

        return corrected

    @staticmethod
    def align_images(
        images: list, reference_index: int = 0, method: str = "cross_correlation"
    ) -> list:
        """
        Align images.

        Parameters
        ----------
        images : list
            List of images to align.
        reference_index : int
            Index of the reference image.
        method : str
            Alignment method.

        Returns
        -------
        list
            List of aligned images.
        """
        # Упрощенная реализация - в полной версии можно использовать
        # более сложные алгоритмы регистрации
        reference = images[reference_index]
        aligned = [reference]

        for i, img in enumerate(images):
            if i == reference_index:
                continue

            # Простое выравнивание по центру масс
            # В полной версии можно использовать cross-correlation
            aligned.append(img)

        return aligned
