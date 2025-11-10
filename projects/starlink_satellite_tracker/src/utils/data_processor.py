#!/usr/bin/env python3
"""
Data processing utilities for Starlink Satellite Tracker
Handles data analysis, filtering, and export functionality
"""

import pandas as pd
import json
import csv
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
import hashlib

# Import our configuration manager
from utils.config_manager import get_config


class DataCache:
    """Enhanced in-memory cache with LRU eviction and time-based expiration."""
    
    def __init__(self, max_size: int = 100, ttl_minutes: int = 30):
        self.cache = {}  # key -> (value, timestamp, access_count)
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve item from cache with TTL check."""
        if key in self.cache:
            value, timestamp, access_count = self.cache[key]
            
            # Check if item has expired
            if datetime.now() - timestamp > self.ttl:
                # Remove expired item
                del self.cache[key]
                self.logger.debug(f"Removed expired cache entry: {key}")
                return None
            
            # Update access count
            self.cache[key] = (value, timestamp, access_count + 1)
            self.logger.debug(f"Cache hit for key: {key}")
            return value
        
        self.logger.debug(f"Cache miss for key: {key}")
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Store item in cache with LRU eviction."""
        # If cache is full, remove least recently used entry
        if len(self.cache) >= self.max_size:
            # Find LRU entry (lowest access count and oldest timestamp)
            lru_key = min(self.cache.keys(), 
                         key=lambda k: (self.cache[k][2], self.cache[k][1]))
            del self.cache[lru_key]
            self.logger.debug(f"Removed LRU cache entry: {lru_key}")
        
        # Store with current timestamp and zero access count
        self.cache[key] = (value, datetime.now(), 0)
        self.logger.debug(f"Added to cache: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.logger.debug("Cache cleared")
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count of removed items."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp, _) in self.cache.items()
            if now - timestamp > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


class DataProcessor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data processor with optional configuration."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Load export configuration
        self.export_config = self.config.get('export', {
            'default_format': 'json',
            'include_tle_data': True,
            'include_predictions': True,
            'compress_large_files': True
        })
        self.data_directory = self.config.get('data_sources', {}).get('tle_cache_path', 'data/tle_cache/')
        
        # Initialize cache with 60-minute TTL
        self.cache = DataCache(max_size=100, ttl_minutes=60)
        
        # Cleanup expired cache entries periodically
        self._last_cleanup = datetime.now()  # Cache expires after 30 minutes
    
    def _generate_cache_key(self, filename: str, criteria: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key based on filename and criteria."""
        key_data = filename
        if criteria:
            # Sort criteria to ensure consistent keys
            sorted_criteria = sorted(criteria.items())
            key_data += str(sorted_criteria)
        
        # Create hash of key data
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def load_satellite_data(self, filename: Optional[str] = None) -> Optional[List[Dict[str, str]]]:
        """Load satellite data from TLE file or cache."""
        try:
            # Periodically cleanup expired cache entries
            self._cleanup_cache_if_needed()
            
            if filename is None:
                # Find the most recent TLE file
                try:
                    files = [f for f in os.listdir(self.data_directory) if f.endswith('.txt')]
                    if not files:
                        self.logger.warning("No TLE files found in directory")
                        return None
                    filename = os.path.join(self.data_directory, sorted(files)[-1])
                except FileNotFoundError:
                    self.logger.error(f"Data directory not found: {self.data_directory}")
                    return None
                except Exception as e:
                    self.logger.error(f"Error listing files in directory {self.data_directory}: {e}")
                    return None
            
            # Ensure filename is not None
            if filename is None:
                self.logger.error("Filename is None")
                return None
                
            if not os.path.exists(filename):
                self.logger.error(f"TLE file not found: {filename}")
                return None
            
            # Check if we have cached data for this file
            cache_key = f"satellite_data_{filename}"
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                self.logger.info(f"Using cached satellite data for {filename}")
                return cached_data
            
            # Load TLE data
            satellites = []
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Process TLE data in groups of 3 lines
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    name = lines[i].strip()
                    line1 = lines[i+1].strip()
                    line2 = lines[i+2].strip()
                    
                    satellites.append({
                        'name': name,
                        'line1': line1,
                        'line2': line2
                    })
            
            # Cache the data
            self.cache.put(cache_key, satellites)
            self.logger.info(f"Loaded {len(satellites)} satellites from {filename} and cached")
            return satellites
            
        except Exception as e:
            self.logger.error(f"Error loading satellite data from {filename}: {e}")
            return None
    
    def filter_satellites(self, satellites: Optional[List[Dict[str, str]]], criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Filter satellites based on provided criteria."""
        # Periodically cleanup expired cache entries
        self._cleanup_cache_if_needed()
        
        if not criteria or not satellites:
            return satellites or []
            
        try:
            # Generate cache key for filtered data
            # For simplicity, we'll use a basic cache key - in a real implementation
            # you might want to serialize the satellites list or use a more sophisticated approach
            cache_key = self._generate_cache_key("filtered", criteria)
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                self.logger.info("Using cached filtered satellite data")
                return cached_result
            
            filtered = []
            for sat in satellites:
                match = True
                for key, value in criteria.items():
                    if key in sat and sat[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(sat)
            
            # Cache the result
            self.cache.put(cache_key, filtered)
            self.logger.info(f"Filtered satellites: {len(satellites)} -> {len(filtered)}")
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error filtering satellites: {e}")
            return satellites or []
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Export satellite data to CSV format."""
        # Periodically cleanup expired cache entries
        self._cleanup_cache_if_needed()
        
        if not data:
            self.logger.warning("No data to export to CSV")
            return False
            
        try:
            # Check cache for export
            cache_key = f"export_csv_{filename}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None and cached_result:
                self.logger.info(f"Using cached CSV export for {filename}")
                return True
            
            compress = self.export_config.get('compress_large_files', True)
            df = pd.DataFrame(data)
            if compress and len(data) > 1000:
                # Compress large files
                df.to_csv(filename + '.gz', index=False, compression='gzip')
                self.logger.info(f"Exported {len(data)} records to {filename}.gz (compressed)")
            else:
                df.to_csv(filename, index=False)
                self.logger.info(f"Exported {len(data)} records to {filename}")
            
            # Cache successful export
            self.cache.put(cache_key, True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {e}")
            return False
    
    def export_to_json(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Export satellite data to JSON format."""
        # Periodically cleanup expired cache entries
        self._cleanup_cache_if_needed()
        
        if not data:
            self.logger.warning("No data to export to JSON")
            return False
            
        try:
            # Check cache for export
            cache_key = f"export_json_{filename}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None and cached_result:
                self.logger.info(f"Using cached JSON export for {filename}")
                return True
            
            compress = self.export_config.get('compress_large_files', True)
            export_data = {
                'satellites': data,
                'exported': datetime.now().isoformat(),
                'count': len(data),
                'version': '1.0'
            }
            
            if compress and len(data) > 1000:
                # Compress large files
                import gzip
                with gzip.open(filename + '.gz', 'wt', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
                self.logger.info(f"Exported {len(data)} records to {filename}.gz (compressed)")
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
                self.logger.info(f"Exported {len(data)} records to {filename}")
            
            # Cache successful export
            self.cache.put(cache_key, True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
            return False
    
    def analyze_constellation(self, satellites: Optional[List[Dict[str, str]]]) -> Dict[str, Any]:
        """Perform basic analysis on the satellite constellation."""
        if not satellites:
            self.logger.warning("No satellites to analyze")
            return {}
            
        try:
            # Check cache for analysis
            cache_key = f"analysis_{len(satellites) if satellites else 0}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                self.logger.info("Using cached constellation analysis")
                return cached_result
            
            # Basic statistics
            stats = {
                'total_satellites': len(satellites),
                'analysis_date': datetime.now().isoformat()
            }
            
            # Extract satellite IDs if possible
            ids = []
            for sat in satellites:
                name = sat.get('name', '')
                if '-' in name:
                    try:
                        # Try to extract numeric ID from name like "STARLINK-1234"
                        id_part = name.split('-')[-1]
                        if id_part.isdigit():
                            ids.append(int(id_part))
                    except Exception as e:
                        self.logger.debug(f"Could not extract ID from satellite name {name}: {e}")
                        pass
            
            if ids:
                stats['id_range'] = {
                    'min': min(ids),
                    'max': max(ids),
                    'count': len(ids)
                }
            
            # Cache the analysis
            self.cache.put(cache_key, stats)
            self.logger.info(f"Analyzed constellation with {len(satellites)} satellites")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error analyzing constellation: {e}")
            return {}
    
    def calculate_satellite_statistics(self, passes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for satellite passes."""
        if not passes:
            self.logger.warning("No passes to analyze for statistics")
            return {}
            
        try:
            # Check cache for statistics
            cache_key = f"pass_stats_{len(passes)}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                self.logger.info("Using cached pass statistics")
                return cached_result
            
            # Calculate statistics
            total_passes = len(passes)
            if total_passes == 0:
                return {}
            
            # Extract values for calculations
            elevations = [p.get('altitude', 0) for p in passes]
            brightnesses = [p.get('brightness', 0) for p in passes]
            distances = [p.get('distance', 0) for p in passes]
            
            # Calculate statistics
            stats = {
                'total_passes': total_passes,
                'average_elevation': sum(elevations) / total_passes if elevations else 0,
                'max_elevation': max(elevations) if elevations else 0,
                'min_elevation': min(elevations) if elevations else 0,
                'average_brightness': sum(brightnesses) / total_passes if brightnesses else 0,
                'average_distance': sum(distances) / total_passes if distances else 0,
                'analysis_date': datetime.now().isoformat()
            }
            
            # Cache the statistics
            self.cache.put(cache_key, stats)
            self.logger.info(f"Calculated statistics for {total_passes} passes")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating satellite statistics: {e}")
            return {}
    
    def _cleanup_cache_if_needed(self) -> None:
        """Periodically cleanup expired cache entries."""
        # Cleanup every 30 minutes
        if datetime.now() - self._last_cleanup > timedelta(minutes=30):
            removed_count = self.cache.cleanup_expired()
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} expired cache entries")
            self._last_cleanup = datetime.now()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self._last_cleanup = datetime.now()
        self.logger.info("Data processor cache cleared")


def main():
    """Example usage of the DataProcessor."""
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize processor
    processor = DataProcessor()
    
    # Load satellite data
    satellites = processor.load_satellite_data()
    
    if satellites:
        print(f"Loaded {len(satellites)} satellites")
        
        # Analyze constellation
        stats = processor.analyze_constellation(satellites)
        print("Constellation Analysis:", stats)
        
        # Export data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export to CSV
        if processor.export_to_csv(satellites, f'starlink_export_{timestamp}.csv'):
            print("CSV export successful")
        else:
            print("CSV export failed")
        
        # Export to JSON
        if processor.export_to_json(satellites, f'starlink_export_{timestamp}.json'):
            print("JSON export successful")
        else:
            print("JSON export failed")
        
        print("Data export completed")
    else:
        print("No satellite data available")


if __name__ == "__main__":
    main()