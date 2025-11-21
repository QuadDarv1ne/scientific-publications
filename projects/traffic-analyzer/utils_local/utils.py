import logging
import os
import time
from typing import Union, Optional, Dict, List, Tuple, Any
import numpy as np
from shapely.geometry import Point, Polygon

logger_profile = logging.getLogger("profile")


def check_and_set_env_var(var_name: str, value_new: Union[str, int]) -> None:
    """
    Проверяет, установлена ли переменная окружения `var_name`. 
    Если не установлена, присваивает ей значение `value_new`.
    
    Args:
        var_name: Имя переменной окружения
        value_new: Значение по умолчанию
    """
    value = os.getenv(var_name)
    if value is None:
        os.environ[var_name] = str(value_new)
        print(f"ℹ️ Значение {value_new} сохранено в переменную окружения {var_name}.")
    else:
        print(f"✅ Переменная {var_name} уже установлена: {value}")


def profile_time(func):
    def exec_and_print_status(*args, **kwargs):
        t_start = time.time()
        out = func(*args, **kwargs)
        t_end = time.time()
        dt_msecs = (t_end - t_start) * 1000

        self = args[0]
        logger_profile.debug(
            f"{self.__class__.__name__}.{func.__name__}, time spent {dt_msecs:.2f} msecs"
        )
        return out

    return exec_and_print_status


class FPS_Counter:
    """
    Счетчик FPS по скользящему окну кадров.
    
    Attributes:
        time_buffer: Буфер временных меток кадров
        calc_time_perion_N_frames: Размер окна для подсчета FPS
    """
    
    def __init__(self, calc_time_perion_N_frames: int) -> None:
        """
        Инициализация счетчика FPS.

        Args:
            calc_time_perion_N_frames: Количество кадров окна подсчета статистики
        """
        self.time_buffer: List[float] = []
        self.calc_time_perion_N_frames = calc_time_perion_N_frames

    def calc_FPS(self) -> float:
        """
        Рассчитывает FPS по нескольким кадрам видео.

        Returns:
            float: Значение FPS или 0.0 если буфер еще не заполнен
        """
        time_buffer_is_full = len(self.time_buffer) == self.calc_time_perion_N_frames
        t = time.time()
        self.time_buffer.append(t)

        if time_buffer_is_full:
            self.time_buffer.pop(0)
            fps = len(self.time_buffer) / (self.time_buffer[-1] - self.time_buffer[0])
            return np.round(fps, 2)
        else:
            return 0.0


def intersects_central_point(
    tracked_xyxy: List[float], 
    polygons: Dict[str, List[float]]
) -> Optional[int]:
    """
    Определяет присутствие центральной точки bbox в области полигонов дорог.

    Args:
        tracked_xyxy: Координаты bounding box [x1, y1, x2, y2]
        polygons: Словарь полигонов дорог {road_id: [x1, y1, x2, y2, ...]}

    Returns:
        Optional[int]: Номер дороги (ключ полигона) или None если не принадлежит ни одному полигону
    """
    # Вычисление центральной точки bbox:
    center_point = [
        (tracked_xyxy[0] + tracked_xyxy[2]) / 2,
        (tracked_xyxy[1] + tracked_xyxy[3]) / 2,
    ]
    center_point = Point(center_point)
    for key, polygon in polygons.items():
        polygon = Polygon([(polygon[i], polygon[i + 1]) for i in range(0, len(polygon), 2)])
        if polygon.contains(center_point):
            return int(key)
    return None
