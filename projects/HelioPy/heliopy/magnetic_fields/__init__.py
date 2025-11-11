"""
Magnetic Fields модули - работа с магнитными полями Солнца.
"""

from heliopy.magnetic_fields.field_extrapolation import FieldExtrapolator
from heliopy.magnetic_fields.field_reconstruction import FieldReconstructor
from heliopy.magnetic_fields.reconnection_detector import ReconnectionDetector
from heliopy.magnetic_fields.topology_analyzer import TopologyAnalyzer

__all__ = [
    "FieldReconstructor",
    "FieldExtrapolator",
    "TopologyAnalyzer",
    "ReconnectionDetector",
]
