"""
Визуализация солнечных изображений.
"""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from heliopy.imaging.image_processor import SolarImage


class ImageVisualizer:
    """Класс для визуализации солнечных изображений."""

    def __init__(self):
        """Инициализация визуализатора."""
        pass

    @staticmethod
    def plot_solar_image(
        image: SolarImage,
        title: Optional[str] = None,
        cmap: str = "sdoaia193",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        save_path: Optional[str] = None,
        **kwargs,
    ) -> plt.Figure:
        """
        Построение изображения Солнца.

        Parameters
        ----------
        image : SolarImage
            Изображение для визуализации.
        title : str, optional
            Заголовок графика.
        cmap : str
            Цветовая карта.
        vmin, vmax : float, optional
            Минимальное и максимальное значения для масштабирования.
        save_path : str, optional
            Путь для сохранения изображения.
        **kwargs
            Дополнительные параметры для matplotlib.

        Returns
        -------
        Figure
            Объект matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        if vmin is None:
            vmin = np.percentile(image.data, 1)
        if vmax is None:
            vmax = np.percentile(image.data, 99)

        im = ax.imshow(image.data, cmap=cmap, vmin=vmin, vmax=vmax, origin="lower", **kwargs)

        if title is None:
            title = f"{image.observatory}/{image.instrument}"
            if image.wavelength:
                title += f" {image.wavelength}Å"
            title += f" - {image.time.iso}"

        ax.set_title(title, fontsize=14)
        ax.set_xlabel("X [pixels]", fontsize=12)
        ax.set_ylabel("Y [pixels]", fontsize=12)

        plt.colorbar(im, ax=ax, label="Intensity")

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        return fig
