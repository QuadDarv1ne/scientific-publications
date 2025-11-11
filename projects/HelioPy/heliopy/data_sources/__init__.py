"""
Data Sources модули - загрузка данных из различных источников.
"""

from heliopy.data_sources.ace_loader import ACELoader
from heliopy.data_sources.goes_loader import GOESLoader
from heliopy.data_sources.omni_loader import OMNILoader
from heliopy.data_sources.sdo_loader import SDOLoader
from heliopy.data_sources.soho_loader import SOHOLoader
from heliopy.data_sources.stereo_loader import STEREOLoader

__all__ = [
    "SDOLoader",
    "SOHOLoader",
    "STEREOLoader",
    "GOESLoader",
    "ACELoader",
    "OMNILoader",
]
