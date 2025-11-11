"""
Создание анимаций солнечных событий.
"""

from typing import List

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from heliopy.imaging.image_processor import SolarImage


class AnimationCreator:
    """Класс для создания анимаций."""

    def __init__(self):
        """Инициализация создателя анимаций."""
        pass

    def create_solar_movie(
        self, images: List[SolarImage], save_path: str, fps: int = 10, **kwargs
    ) -> None:
        """
        Создание фильма из последовательности изображений.

        Parameters
        ----------
        images : list
            Список изображений.
        save_path : str
            Путь для сохранения анимации.
        fps : int
            Кадров в секунду.
        **kwargs
            Дополнительные параметры.
        """
        if len(images) == 0:
            raise ValueError("Список изображений пуст")

        fig, ax = plt.subplots(figsize=(10, 10))

        # Настройка первого кадра
        vmin = np.percentile(images[0].data, 1)
        vmax = np.percentile(images[0].data, 99)

        im = ax.imshow(images[0].data, cmap="sdoaia193", vmin=vmin, vmax=vmax, origin="lower")
        ax.set_title(f"{images[0].observatory}/{images[0].instrument} - {images[0].time.iso}")

        def animate(frame):
            im.set_array(images[frame].data)
            ax.set_title(
                f"{images[frame].observatory}/{images[frame].instrument} - {images[frame].time.iso}"
            )
            return [im]

        anim = animation.FuncAnimation(
            fig, animate, frames=len(images), interval=1000 / fps, blit=True, repeat=True
        )

        anim.save(save_path, writer="ffmpeg", fps=fps)
        plt.close(fig)
