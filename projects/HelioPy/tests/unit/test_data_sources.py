"""
Модульные тесты для data_sources модулей.
"""

import pytest
from pathlib import Path


class TestDataSourcesModule:
    """Тесты для модуля data_sources."""

    def test_import_base_loader(self):
        """Тест импорта базового загрузчика."""
        from heliopy.data_sources.base_loader import BaseLoader

        assert BaseLoader is not None

    def test_import_sdo_loader(self):
        """Тест импорта SDO загрузчика."""
        from heliopy.data_sources.sdo_loader import SDOLoader

        assert SDOLoader is not None

    def test_sdo_loader_wavelengths(self):
        """Тест списка поддерживаемых длин волн AIA."""
        from heliopy.data_sources.sdo_loader import SDOLoader

        assert hasattr(SDOLoader, "AIA_WAVELENGTHS")
        assert 193 in SDOLoader.AIA_WAVELENGTHS
        assert 171 in SDOLoader.AIA_WAVELENGTHS
