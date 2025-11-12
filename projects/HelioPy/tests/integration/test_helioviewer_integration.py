"""
Integration tests for Helioviewer functionality in core data loader.
"""

import unittest
from unittest.mock import patch, MagicMock

from heliopy.core.data_loader import DataLoader


class TestHelioviewerIntegration(unittest.TestCase):
    """Integration tests for Helioviewer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_loader = DataLoader()

    def test_helioviewer_loader_initialization(self):
        """Test that Helioviewer loader is properly initialized."""
        self.assertTrue(hasattr(self.data_loader, 'helioviewer_loader'))

    @patch('heliopy.data_sources.helioviewer_loader.HelioviewerLoader.get_data_sources')
    def test_get_helioviewer_sources(self, mock_get_sources):
        """Test get_helioviewer_sources method."""
        # Mock the return value
        mock_get_sources.return_value = {"test": "data"}
        
        # Test the method
        result = self.data_loader.get_helioviewer_sources()
        
        # Verify the result
        self.assertEqual(result, {"test": "data"})
        mock_get_sources.assert_called_once()

    @patch('heliopy.data_sources.helioviewer_loader.HelioviewerLoader.load_image')
    def test_load_helioviewer(self, mock_load_image):
        """Test load_helioviewer method."""
        # Mock the return value
        mock_image = MagicMock()
        mock_load_image.return_value = mock_image
        
        # Test the method
        result = self.data_loader.load_helioviewer("2023-10-15", 14)
        
        # Verify the result
        self.assertEqual(result, mock_image)
        mock_load_image.assert_called_once_with("2023-10-15", 14)


if __name__ == '__main__':
    unittest.main()