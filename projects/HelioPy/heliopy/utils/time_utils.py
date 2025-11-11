"""
Utilities for working with time in heliophysics.
"""

from datetime import datetime, timedelta
from typing import Union

import numpy as np
from astropy import units as u
from astropy.time import Time


class TimeUtils:
    """Utilities for working with time."""

    @staticmethod
    def parse_time(time_input: Union[str, datetime, Time]) -> Time:
        """
        Parse time in various formats.

        Parameters
        ----------
        time_input : str, datetime, or Time
            Time in various formats.

        Returns
        -------
        Time
            Astropy Time object.
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
        Generate time array in a given range.

        Parameters
        ----------
        start : str, datetime, or Time
            Start time.
        end : str, datetime, or Time
            End time.
        step : timedelta or Quantity
            Time step.

        Returns
        -------
        np.ndarray
            Array of Time objects.
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
        Convert Time to datetime.

        Parameters
        ----------
        time : Time
            Time in astropy Time format.

        Returns
        -------
        datetime
            Time in datetime format.
        """
        return time.datetime

    @staticmethod
    def to_julian_date(time: Union[str, datetime, Time]) -> float:
        """
        Convert time to Julian date.

        Parameters
        ----------
        time : str, datetime, or Time
            Time.

        Returns
        -------
        float
            Julian date.
        """
        time_obj = TimeUtils.parse_time(time)
        return time_obj.jd

    @staticmethod
    def carrington_rotation(time: Union[str, datetime, Time]) -> float:
        """
        Calculate Carrington rotation number.

        Parameters
        ----------
        time : str, datetime, or Time
            Time.

        Returns
        -------
        float
            Carrington rotation number.
        """
        time_obj = TimeUtils.parse_time(time)
        # Эпоха первого вращения Кэррингтона: 1853-11-09 12:00:00
        carrington_epoch = Time("1853-11-09 12:00:00")
        days_since_epoch = (time_obj - carrington_epoch).jd
        rotation_number = 1 + days_since_epoch / 27.2753
        return rotation_number
