"""
HelioPy - Open-source библиотека для анализа солнечной активности и прогнозирования космической погоды.

HelioPy предоставляет единый интерфейс для работы с данными от различных космических миссий
и наземных обсерваторий, а также включает инструменты для научного анализа и визуализации.
"""

__version__ = "0.1.0"
__author__ = "Dupley Maxim Igorevich"
__license__ = "Custom License by Programming School Maestro7IT"

# Основные импорты
from heliopy import core
from heliopy import events
from heliopy import imaging
from heliopy import space_weather
from heliopy import visualization

__all__ = [
    "core",
    "events",
    "imaging",
    "space_weather",
    "visualization",
]

