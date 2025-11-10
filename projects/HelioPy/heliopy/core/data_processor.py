"""
Обработка и предобработка данных.
"""

import numpy as np
from typing import Optional, Union, Tuple
from astropy import units as u
from scipy import ndimage
from skimage import filters, restoration


class DataProcessor:
    """Класс для обработки и предобработки данных."""
    
    def __init__(self):
        """Инициализация процессора данных."""
        pass
    
    @staticmethod
    def normalize(data: np.ndarray, 
                  method: str = 'minmax',
                  vmin: Optional[float] = None,
                  vmax: Optional[float] = None) -> np.ndarray:
        """
        Нормализация данных.
        
        Parameters
        ----------
        data : array
            Входные данные.
        method : str
            Метод нормализации ('minmax', 'zscore', 'log').
        vmin, vmax : float, optional
            Минимальное и максимальное значения для minmax нормализации.
        
        Returns
        -------
        array
            Нормализованные данные.
        """
        if method == 'minmax':
            if vmin is None:
                vmin = np.nanmin(data)
            if vmax is None:
                vmax = np.nanmax(data)
            if vmax == vmin:
                return np.zeros_like(data)
            return (data - vmin) / (vmax - vmin)
        
        elif method == 'zscore':
            mean = np.nanmean(data)
            std = np.nanstd(data)
            if std == 0:
                return np.zeros_like(data)
            return (data - mean) / std
        
        elif method == 'log':
            data_positive = np.maximum(data, np.finfo(float).eps)
            return np.log10(data_positive)
        
        else:
            raise ValueError(f"Неизвестный метод нормализации: {method}")
    
    @staticmethod
    def remove_background(data: np.ndarray, 
                         method: str = 'median',
                         kernel_size: int = 50) -> np.ndarray:
        """
        Удаление фона из изображения.
        
        Parameters
        ----------
        data : array
            Входное изображение.
        method : str
            Метод удаления фона ('median', 'gaussian', 'morphological').
        kernel_size : int
            Размер ядра для фильтрации.
        
        Returns
        -------
        array
            Изображение с удаленным фоном.
        """
        if method == 'median':
            background = ndimage.median_filter(data, size=kernel_size)
        elif method == 'gaussian':
            background = filters.gaussian(data, sigma=kernel_size/3)
        elif method == 'morphological':
            from skimage.morphology import disk
            background = ndimage.grey_opening(data, structure=disk(kernel_size))
        else:
            raise ValueError(f"Неизвестный метод: {method}")
        
        return data - background
    
    @staticmethod
    def denoise(data: np.ndarray,
                method: str = 'gaussian',
                sigma: float = 1.0) -> np.ndarray:
        """
        Удаление шума из данных.
        
        Parameters
        ----------
        data : array
            Входные данные с шумом.
        method : str
            Метод удаления шума ('gaussian', 'bilateral', 'tv').
        sigma : float
            Параметр сглаживания.
        
        Returns
        -------
        array
            Данные без шума.
        """
        if method == 'gaussian':
            return filters.gaussian(data, sigma=sigma)
        elif method == 'bilateral':
            return restoration.denoise_bilateral(data, sigma_color=sigma, sigma_spatial=sigma)
        elif method == 'tv':
            return restoration.denoise_tv_chambolle(data, weight=sigma)
        else:
            raise ValueError(f"Неизвестный метод: {method}")
    
    @staticmethod
    def calibrate_flux(data: np.ndarray,
                      exposure_time: float,
                      calibration_factor: float = 1.0) -> np.ndarray:
        """
        Калибровка потока излучения.
        
        Parameters
        ----------
        data : array
            Сырые данные детектора.
        exposure_time : float
            Время экспозиции в секундах.
        calibration_factor : float
            Калибровочный коэффициент.
        
        Returns
        -------
        array
            Калиброванные данные.
        """
        return (data / exposure_time) * calibration_factor
    
    @staticmethod
    def correct_limb_darkening(data: np.ndarray,
                              center: Optional[Tuple[int, int]] = None,
                              radius: Optional[float] = None) -> np.ndarray:
        """
        Коррекция потемнения к краю диска.
        
        Parameters
        ----------
        data : array
            Входное изображение.
        center : tuple, optional
            Центр диска (x, y). Если не указан, вычисляется автоматически.
        radius : float, optional
            Радиус диска. Если не указан, вычисляется автоматически.
        
        Returns
        -------
        array
            Изображение с коррекцией потемнения к краю.
        """
        if center is None:
            center = (data.shape[1] // 2, data.shape[0] // 2)
        
        if radius is None:
            radius = min(data.shape) / 2
        
        y, x = np.ogrid[:data.shape[0], :data.shape[1]]
        r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
        
        # Маска для диска
        mask = r <= radius
        
        # Модель потемнения к краю (упрощенная)
        mu = np.sqrt(1 - (r / radius)**2)
        mu = np.maximum(mu, 0.1)  # Избегаем деления на ноль
        
        # Коррекция
        corrected = data.copy()
        corrected[mask] = data[mask] / mu[mask]
        
        return corrected
    
    @staticmethod
    def align_images(images: list,
                    reference_index: int = 0,
                    method: str = 'cross_correlation') -> list:
        """
        Выравнивание изображений.
        
        Parameters
        ----------
        images : list
            Список изображений для выравнивания.
        reference_index : int
            Индекс опорного изображения.
        method : str
            Метод выравнивания.
        
        Returns
        -------
        list
            Список выровненных изображений.
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

