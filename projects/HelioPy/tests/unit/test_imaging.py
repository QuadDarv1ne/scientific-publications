"""
Модульные тесты для imaging и visualization модулей.
"""

import pytest
import numpy as np


class TestImagingModule:
    """Тесты для модуля imaging."""

    def test_import_image_processor(self):
        """Тест импорта ImageProcessor."""
        from heliopy.imaging.image_processor import ImageProcessor

        assert ImageProcessor is not None

    def test_image_processor_initialization(self):
        """Тест инициализации ImageProcessor."""
        from heliopy.imaging.image_processor import ImageProcessor

        processor = ImageProcessor()
        assert processor is not None

    def test_import_feature_extractor(self):
        """Тест импорта FeatureExtractor."""
        from heliopy.imaging.feature_extractor import FeatureExtractor

        assert FeatureExtractor is not None
