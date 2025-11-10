#!/usr/bin/env python3
"""
Data processing utilities for Starlink Satellite Tracker
Handles data analysis, filtering, and export functionality
"""

import pandas as pd
import json
import csv
import os
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional

# Import our configuration manager
from utils.config_manager import get_config


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
        
    def load_satellite_data(self, filename: Optional[str] = None) -> Optional[List[Dict[str, str]]]:
        """Load satellite data from TLE file or cache."""
        try:
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
            
            if not os.path.exists(filename):
                self.logger.error(f"TLE file not found: {filename}")
                return None
                
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
            
            self.logger.info(f"Loaded {len(satellites)} satellites from {filename}")
            return satellites
            
        except Exception as e:
            self.logger.error(f"Error loading satellite data from {filename}: {e}")
            return None
    
    def filter_satellites(self, satellites: Optional[List[Dict[str, str]]], criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Filter satellites based on provided criteria."""
        if not criteria or not satellites:
            return satellites or []
            
        try:
            filtered = []
            for sat in satellites:
                match = True
                for key, value in criteria.items():
                    if key in sat and sat[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(sat)
                    
            self.logger.info(f"Filtered satellites: {len(satellites)} -> {len(filtered)}")
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error filtering satellites: {e}")
            return satellites or []
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Export satellite data to CSV format."""
        if not data:
            self.logger.warning("No data to export to CSV")
            return False
            
        try:
            compress = self.export_config.get('compress_large_files', True)
            df = pd.DataFrame(data)
            if compress and len(data) > 1000:
                # Compress large files
                df.to_csv(filename + '.gz', index=False, compression='gzip')
                self.logger.info(f"Exported {len(data)} records to {filename}.gz (compressed)")
            else:
                df.to_csv(filename, index=False)
                self.logger.info(f"Exported {len(data)} records to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {e}")
            return False
    
    def export_to_json(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Export satellite data to JSON format."""
        if not data:
            self.logger.warning("No data to export to JSON")
            return False
            
        try:
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
            
            self.logger.info(f"Analyzed constellation with {len(satellites)} satellites")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error analyzing constellation: {e}")
            return {}


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