"""
HelioPy - Open-source library for solar activity analysis and space weather forecasting.

HelioPy provides a unified interface for working with data from various space missions
and ground-based observatories, as well as tools for scientific analysis and visualization.

Modules:
    - core: Core data processing functions
    - data_sources: Data loaders from various sources
    - events: Solar event detectors
    - imaging: Image processing
    - magnetic_fields: Magnetic field analysis
    - models: Forecasting models
    - space_weather: Space weather
    - utils: Utility functions
    - visualization: Data visualization
"""

__version__ = "0.1.0"
__author__ = "Dupley Maxim Igorevich"
__license__ = "Custom License by Programming School Maestro7IT"

# Основные импорты
from heliopy import core, events, imaging, space_weather, visualization

# Удобные функции для быстрого доступа
from heliopy.core.data_loader import load_goes, load_helioviewer, load_psp_fld, load_psp_sweap, load_sdo_aia, load_soho_lasco
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
    "load_helioviewer",
    "load_psp_sweap",
    "load_psp_fld",
    "forecast_geoeffectiveness",
]
