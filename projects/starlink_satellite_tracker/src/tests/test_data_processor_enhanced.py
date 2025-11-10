#!/usr/bin/env python3
"""
Test suite for Enhanced Data Processor
Verifies the enhanced caching functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.data_processor import DataCache


class TestDataCache(unittest.TestCase):
    """Test suite for enhanced DataCache class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.cache = DataCache(max_size=5, ttl_minutes=10)

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = DataCache(max_size=10, ttl_minutes=30)
        self.assertEqual(cache.max_size, 10)
        self.assertEqual(cache.size(), 0)

    def test_cache_put_and_get(self):
        """Test putting and getting items from cache."""
        # Test putting an item
        self.cache.put("key1", "value1")
        self.assertEqual(self.cache.size(), 1)
        
        # Test getting the item
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
        
        # Test getting non-existent item
        value = self.cache.get("nonexistent")
        self.assertIsNone(value)

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        for i in range(5):
            self.cache.put(f"key{i}", f"value{i}")
        
        self.assertEqual(self.cache.size(), 5)
        
        # Add one more item, should evict LRU item
        self.cache.put("key5", "value5")
        self.assertEqual(self.cache.size(), 5)  # Size should remain the same
        
        # The first item should be evicted (LRU)
        value = self.cache.get("key0")
        self.assertIsNone(value)
        
        # New item should be accessible
        value = self.cache.get("key5")
        self.assertEqual(value, "value5")

    def test_cache_ttl_expiration(self):
        """Test TTL expiration of cache entries."""
        # Put an item in cache
        self.cache.put("key1", "value1")
        
        # Should be able to retrieve it
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
        
        # Manually expire the item by modifying its timestamp
        # This is a bit hacky but necessary for testing
        with patch('utils.data_processor.datetime') as mock_datetime:
            # Set future time to simulate expiration
            future_time = datetime.now() + timedelta(minutes=15)
            mock_datetime.now.return_value = future_time
            
            # Try to get the item, should return None due to expiration
            value = self.cache.get("key1")
            self.assertIsNone(value)

    def test_cache_cleanup_expired(self):
        """Test cleanup of expired entries."""
        # Put items in cache
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        self.assertEqual(self.cache.size(), 2)
        
        # Manually expire items and cleanup
        with patch('utils.data_processor.datetime') as mock_datetime:
            # Set future time to simulate expiration
            future_time = datetime.now() + timedelta(minutes=15)
            mock_datetime.now.return_value = future_time
            
            # Cleanup expired entries
            removed_count = self.cache.cleanup_expired()
            self.assertEqual(removed_count, 2)
            self.assertEqual(self.cache.size(), 0)

    def test_cache_clear(self):
        """Test clearing all cache entries."""
        # Put items in cache
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        self.assertEqual(self.cache.size(), 2)
        
        # Clear cache
        self.cache.clear()
        self.assertEqual(self.cache.size(), 0)
        
        # Try to get items, should return None
        value = self.cache.get("key1")
        self.assertIsNone(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)