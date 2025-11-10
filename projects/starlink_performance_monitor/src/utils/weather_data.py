#!/usr/bin/env python3
"""
Starlink Performance Monitor
Weather data integration module for performance correlation analysis.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Try to import openmeteo_requests, but don't fail if it's not available
OPENMETEO_AVAILABLE = False
try:
    import openmeteo_requests
    import requests_cache
    import pandas as pd
    from retry_requests import retry
    OPENMETEO_AVAILABLE = True
except ImportError:
    openmeteo_requests = None
    requests_cache = None
    pd = None
    retry = None

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.utils.logging_config import get_logger
from src.database.db_manager import get_database_manager, get_db_session
from src.database.models import WeatherData, Base


class WeatherDataCollector:
    """Collect and store weather data for correlation analysis with performance metrics."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the weather data collector with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.client = self._setup_client() if OPENMETEO_AVAILABLE else None
        self.db_manager = get_database_manager(config_path)
        self.db_engine = self.db_manager.get_engine()
        # Create tables if they don't exist
        Base.metadata.create_all(self.db_engine)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def _setup_client(self):
        """Set up the Open-Meteo API client."""
        if not OPENMETEO_AVAILABLE:
            self.logger.warning("Open-Meteo dependencies not available")
            return None
            
        try:
            # Setup the Open-Meteo API client using the requests-cache and retry-requests libraries
            cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
            retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
            return openmeteo_requests.Client(session=retry_session)
        except Exception as e:
            self.logger.error(f"Failed to set up Open-Meteo client: {e}")
            return None
            
    def get_weather_data(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Get weather data for correlation analysis.
        
        Args:
            start_date: Start date for weather data (defaults to 7 days ago)
            end_date: End date for weather data (defaults to now)
            
        Returns:
            Dictionary with weather data or None if failed
        """
        if not self.client or not OPENMETEO_AVAILABLE:
            self.logger.warning("Open-Meteo client not available")
            return None
            
        try:
            # Get weather configuration
            weather_config = self.config.get('weather', {})
            if not weather_config.get('enabled', False):
                self.logger.info("Weather data collection is disabled")
                return None
                
            # Get location
            location = weather_config.get('location', {})
            latitude = location.get('latitude', 0.0)
            longitude = location.get('longitude', 0.0)
            
            # Set default dates if not provided
            if end_date is None:
                end_date = datetime.utcnow()
            if start_date is None:
                start_date = end_date - timedelta(days=7)
                
            # Format dates for API
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Get parameters
            parameters = weather_config.get('parameters', [
                "temperature_2m", 
                "precipitation", 
                "wind_speed_10m", 
                "cloud_cover"
            ])
            
            self.logger.info(f"Fetching weather data for {latitude}, {longitude} from {start_date_str} to {end_date_str}")
            
            # Setup the Open-Meteo API parameters
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "hourly": parameters
            }
            
            # Fetch weather data
            responses = self.client.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)
            
            # Process the response
            if responses and len(responses) > 0:
                response = responses[0]
                
                # Extract hourly data
                hourly = response.Hourly()
                hourly_data = {"date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )}
                
                # Add each parameter
                for i, param in enumerate(parameters):
                    hourly_data[param] = hourly.Variables(i).ValuesAsNumpy()
                
                # Convert to DataFrame
                hourly_dataframe = pd.DataFrame(data=hourly_data)
                
                # Convert to dictionary format for storage
                weather_data = []
                for _, row in hourly_dataframe.iterrows():
                    record = {
                        'timestamp': row['date'].isoformat(),
                    }
                    for param in parameters:
                        record[param] = float(row[param]) if not pd.isna(row[param]) else None
                    weather_data.append(record)
                
                self.logger.info(f"Successfully fetched {len(weather_data)} weather records")
                
                # Store weather data in database
                self._store_weather_data(weather_data, latitude, longitude)
                
                return {
                    'location': {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'data': weather_data
                }
            else:
                self.logger.warning("No weather data received from API")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching weather data: {e}")
            return None
            
    def _store_weather_data(self, weather_data: List[Dict[str, Any]], latitude: float, longitude: float):
        """
        Store weather data in the database.
        
        Args:
            weather_data: List of weather data records
            latitude: Latitude of the location
            longitude: Longitude of the location
        """
        try:
            session = get_db_session()
            
            # Store each weather record
            for record in weather_data:
                try:
                    timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                    
                    weather_record = WeatherData(
                        timestamp=timestamp,
                        latitude=latitude,
                        longitude=longitude,
                        temperature_2m=record.get('temperature_2m'),
                        precipitation=record.get('precipitation'),
                        wind_speed_10m=record.get('wind_speed_10m'),
                        cloud_cover=record.get('cloud_cover'),
                        pressure_msl=record.get('pressure_msl'),
                        humidity_2m=record.get('humidity_2m')
                    )
                    
                    session.add(weather_record)
                except Exception as e:
                    self.logger.warning(f"Failed to store weather record: {e}")
                    continue
            
            session.commit()
            self.logger.info(f"Stored {len(weather_data)} weather records in database")
            
        except Exception as e:
            self.logger.error(f"Error storing weather data: {e}")
            if 'session' in locals():
                session.rollback()
        finally:
            if 'session' in locals():
                session.close()
            
    def correlate_with_performance(self, weather_data: Dict[str, Any], performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Correlate weather data with performance metrics.
        
        Args:
            weather_data: Weather data from get_weather_data
            performance_data: Performance metrics data
            
        Returns:
            Dictionary with correlation analysis results
        """
        if not pd or not OPENMETEO_AVAILABLE:
            self.logger.warning("Pandas not available for correlation analysis")
            return {}
            
        try:
            # Convert data to DataFrames
            weather_df = pd.DataFrame(weather_data['data'])
            performance_df = pd.DataFrame(performance_data)
            
            # Convert timestamps to datetime
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            performance_df['timestamp'] = pd.to_datetime(performance_df['timestamp'])
            
            # Merge dataframes on timestamp (nearest match)
            merged_df = pd.merge_asof(
                performance_df.sort_values('timestamp'),
                weather_df.sort_values('timestamp'),
                on='timestamp',
                direction='nearest',
                tolerance=pd.Timedelta('1H')  # Match within 1 hour
            )
            
            # Calculate correlations
            correlations = {}
            weather_params = [col for col in weather_df.columns if col != 'timestamp']
            performance_params = ['download_mbps', 'upload_mbps', 'ping_ms', 'packet_loss_percent']
            
            for weather_param in weather_params:
                if weather_param in merged_df.columns:
                    correlations[weather_param] = {}
                    for perf_param in performance_params:
                        if perf_param in merged_df.columns:
                            # Calculate correlation coefficient
                            corr = merged_df[weather_param].corr(merged_df[perf_param])
                            correlations[weather_param][perf_param] = float(corr) if not pd.isna(corr) else 0.0
            
            self.logger.info("Correlation analysis completed")
            return {
                'correlations': correlations,
                'analysis_period': {
                    'start': merged_df['timestamp'].min().isoformat() if not merged_df.empty else None,
                    'end': merged_df['timestamp'].max().isoformat() if not merged_df.empty else None
                },
                'data_points': len(merged_df)
            }
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}")
            return {}


def main():
    """Main entry point for testing weather data collection."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Weather Data Collector')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Parse dates if provided
    start_date = None
    end_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    # Initialize collector
    collector = WeatherDataCollector(args.config)
    
    # Fetch weather data
    weather_data = collector.get_weather_data(start_date, end_date)
    
    if weather_data:
        print(f"Successfully fetched weather data for {len(weather_data['data'])} time points")
        print(f"Location: {weather_data['location']['latitude']}, {weather_data['location']['longitude']}")
        
        # Show first few records
        print("\nFirst 5 weather records:")
        for i, record in enumerate(weather_data['data'][:5]):
            print(f"  {record}")
    else:
        print("Failed to fetch weather data")


if __name__ == "__main__":
    main()