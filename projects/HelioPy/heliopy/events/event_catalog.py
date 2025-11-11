"""
Работа с каталогами событий.
"""

from typing import List

import pandas as pd
from astropy.time import Time

from heliopy.events.cme_detector import CME
from heliopy.events.flare_detector import Flare


class EventCatalog:
    """Класс для работы с каталогами событий."""

    def __init__(self):
        """Инициализация каталога."""
        self.flares: List[Flare] = []
        self.cmes: List[CME] = []

    def add_flare(self, flare: Flare):
        """Добавление вспышки в каталог."""
        self.flares.append(flare)

    def add_cme(self, cme: CME):
        """Добавление CME в каталог."""
        self.cmes.append(cme)

    def get_flares_by_class(self, flare_class: str) -> List[Flare]:
        """
        Получение вспышек по классу.

        Parameters
        ----------
        flare_class : str
            Класс вспышки (A, B, C, M, X).

        Returns
        -------
        list
            Список вспышек указанного класса.
        """
        return [f for f in self.flares if f.class_ == flare_class]

    def get_flares_by_time_range(self, start_time: Time, end_time: Time) -> List[Flare]:
        """
        Получение вспышек в заданном временном диапазоне.

        Parameters
        ----------
        start_time, end_time : Time
            Начальное и конечное время.

        Returns
        -------
        list
            Список вспышек в диапазоне.
        """
        return [f for f in self.flares if start_time <= f.start_time <= end_time]

    def to_dataframe(self) -> pd.DataFrame:
        """
        Преобразование каталога в DataFrame.

        Returns
        -------
        DataFrame
            DataFrame с событиями.
        """
        data = []

        for flare in self.flares:
            data.append(
                {
                    "type": "flare",
                    "start_time": flare.start_time,
                    "peak_time": flare.peak_time,
                    "end_time": flare.end_time,
                    "class": flare.class_,
                    "peak_flux": flare.peak_flux,
                    "duration": flare.duration,
                }
            )

        for cme in self.cmes:
            data.append(
                {
                    "type": "cme",
                    "start_time": cme.start_time,
                    "speed": cme.speed,
                    "acceleration": cme.acceleration,
                    "direction_lon": cme.direction["lon"],
                    "direction_lat": cme.direction["lat"],
                    "angular_width": cme.angular_width,
                }
            )

        return pd.DataFrame(data)
