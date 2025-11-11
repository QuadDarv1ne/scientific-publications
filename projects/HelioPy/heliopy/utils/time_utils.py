"""
Утилиты для работы со временем в гелиофизике.
"""

from datetime import datetime, timedelta
from typing import Union

import numpy as np
from astropy import units as u
from astropy.time import Time


class TimeUtils:
    """Утилиты для работы со временем."""

    @staticmethod
    def parse_time(time_input: Union[str, datetime, Time]) -> Time:
        """
        Парсинг времени в различных форматах.

        Parameters
        ----------
        time_input : str, datetime, или Time
            Время в различных форматах.

        Returns
        -------
        Time
            Объект astropy Time.
        """
        if isinstance(time_input, Time):
            return time_input
        elif isinstance(time_input, datetime) or isinstance(time_input, str):
            return Time(time_input)
        else:
            raise ValueError(f"Неподдерживаемый тип времени: {type(time_input)}")

    @staticmethod
    def time_range(
        start: Union[str, datetime, Time],
        end: Union[str, datetime, Time],
        step: Union[timedelta, u.Quantity] = timedelta(hours=1),
    ) -> np.ndarray:
        """
        Генерация массива времени в заданном диапазоне.

        Parameters
        ----------
        start : str, datetime, или Time
            Начальное время.
        end : str, datetime, или Time
            Конечное время.
        step : timedelta или Quantity
            Шаг времени.

        Returns
        -------
        np.ndarray
            Массив объектов Time.
        """
        start_time = TimeUtils.parse_time(start)
        end_time = TimeUtils.parse_time(end)

        if isinstance(step, timedelta):
            step_seconds = step.total_seconds()
        else:
            step_seconds = step.to(u.s).value

        times = []
        current = start_time
        while current <= end_time:
            times.append(current)
            current = Time(current.jd + step_seconds / 86400, format="jd")

        return np.array(times)

    @staticmethod
    def to_datetime(time: Time) -> datetime:
        """
        Преобразование Time в datetime.

        Parameters
        ----------
        time : Time
            Время в формате astropy Time.

        Returns
        -------
        datetime
            Время в формате datetime.
        """
        return time.datetime

    @staticmethod
    def to_julian_date(time: Union[str, datetime, Time]) -> float:
        """
        Преобразование времени в юлианскую дату.

        Parameters
        ----------
        time : str, datetime, или Time
            Время.

        Returns
        -------
        float
            Юлианская дата.
        """
        time_obj = TimeUtils.parse_time(time)
        return time_obj.jd

    @staticmethod
    def carrington_rotation(time: Union[str, datetime, Time]) -> float:
        """
        Вычисление номера вращения Кэррингтона.

        Parameters
        ----------
        time : str, datetime, или Time
            Время.

        Returns
        -------
        float
            Номер вращения Кэррингтона.
        """
        time_obj = TimeUtils.parse_time(time)
        # Эпоха первого вращения Кэррингтона: 1853-11-09 12:00:00
        carrington_epoch = Time("1853-11-09 12:00:00")
        days_since_epoch = (time_obj - carrington_epoch).jd
        rotation_number = 1 + days_since_epoch / 27.2753
        return rotation_number
