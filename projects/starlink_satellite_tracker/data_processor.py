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

class DataProcessor:
    def __init__(self, config=None):
        """Initialize data processor with optional configuration."""
        self.config = config or {}
        self.data_directory = self.config.get('data_sources', {}).get('tle_cache_path', 'data/tle_cache/')
        
    def load_satellite_data(self, filename=None):
        """Load satellite data from TLE file or cache."""
        if filename is None:
            # Find the most recent TLE file
            try:
                files = [f for f in os.listdir(self.data_directory) if f.endswith('.txt')]
                if not files:
                    return None
                filename = os.path.join(self.data_directory, sorted(files)[-1])
            except FileNotFoundError:
                return None
        
        if not os.path.exists(filename):
            return None
            
        # Load TLE data
        satellites = []
        with open(filename, 'r') as f:
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
        
        return satellites
    
    def filter_satellites(self, satellites, criteria=None):
        """Filter satellites based on provided criteria."""
        if not criteria or not satellites:
            return satellites
            
        filtered = []
        for sat in satellites:
            match = True
            for key, value in criteria.items():
                if key in sat and sat[key] != value:
                    match = False
                    break
            if match:
                filtered.append(sat)
                
        return filtered
    
    def export_to_csv(self, data, filename):
        """Export satellite data to CSV format."""
        if not data:
            return False
            
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logging.info(f"Exported {len(data)} records to {filename}")
            return True
        except Exception as e:
            logging.error(f"Failed to export to CSV: {e}")
            return False
    
    def export_to_json(self, data, filename):
        """Export satellite data to JSON format."""
        if not data:
            return False
            
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'satellites': data,
                    'exported': datetime.now().isoformat(),
                    'count': len(data)
                }, f, indent=2)
            logging.info(f"Exported {len(data)} records to {filename}")
            return True
        except Exception as e:
            logging.error(f"Failed to export to JSON: {e}")
            return False
    
    def analyze_constellation(self, satellites):
        """Perform basic analysis on the satellite constellation."""
        if not satellites:
            return {}
            
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
                except:
                    pass
        
        if ids:
            stats['id_range'] = {
                'min': min(ids),
                'max': max(ids),
                'count': len(ids)
            }
        
        return stats

def main():
    """Example usage of the DataProcessor."""
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
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
        processor.export_to_csv(satellites, f'starlink_export_{timestamp}.csv')
        
        # Export to JSON
        processor.export_to_json(satellites, f'starlink_export_{timestamp}.json')
        
        print("Data exported successfully")
    else:
        print("No satellite data available")

if __name__ == "__main__":
    main()