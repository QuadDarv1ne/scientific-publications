"""
Events модули - обнаружение и анализ солнечных событий.
"""

from heliopy.events.flare_detector import FlareDetector
from heliopy.events.cme_detector import CMEDetector
from heliopy.events.event_catalog import EventCatalog
from heliopy.events.event_analyzer import EventAnalyzer

__all__ = [
    "FlareDetector",
    "CMEDetector",
    "EventCatalog",
    "EventAnalyzer",
]

