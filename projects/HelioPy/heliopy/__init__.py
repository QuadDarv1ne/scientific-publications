"""
HelioPy - Open-source библиотека для анализа солнечной активности и прогнозирования космической погоды.

HelioPy предоставляет единый интерфейс для работы с данными от различных космических миссий
и наземных обсерваторий, а также включает инструменты для научного анализа и визуализации.
"""

__version__ = "0.1.0"
__author__ = "Dupley Maxim Igorevich"
__license__ = "Custom License by Programming School Maestro7IT"

# Основные импорты
from heliopy import core, events, imaging, space_weather, visualization

# Удобные функции для быстрого доступа
from heliopy.core.data_loader import load_goes, load_sdo_aia, load_soho_lasco
from heliopy.space_weather.forecast_models import forecast_geoeffectiveness

__all__ = [
    "core",
    "events",
    "imaging",
    "space_weather",
    "visualization",
    "load_sdo_aia",
    "load_soho_lasco",
    "load_goes",
    "forecast_geoeffectiveness",
]
