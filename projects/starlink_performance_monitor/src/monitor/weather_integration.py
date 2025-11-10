#!/usr/bin/env python3
"""
Starlink Performance Monitor
Weather data integration with performance monitoring.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.weather_data import WeatherDataCollector
from src.utils.logging_config import get_logger
from src.database.db_manager import get_db_session
from src.monitor.monitor import PerformanceMetric
from src.database.models import WeatherData


class WeatherPerformanceAnalyzer:
    """Analyze correlation between weather data and performance metrics."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the weather-performance analyzer with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.weather_collector = WeatherDataCollector(config_path)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def get_performance_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get performance data for correlation analysis.
        
        Args:
            start_date: Start date for performance data
            end_date: End date for performance data
            
        Returns:
            List of performance data records
        """
        session = get_db_session()
        try:
            # Query performance metrics within the date range
            metrics = session.query(PerformanceMetric).filter(
                PerformanceMetric.timestamp >= start_date,
                PerformanceMetric.timestamp <= end_date
            ).order_by(PerformanceMetric.timestamp).all()
            
            # Convert to dictionary format
            performance_data = []
            for metric in metrics:
                performance_data.append({
                    'timestamp': metric.timestamp,
                    'download_mbps': float(metric.download_mbps) if metric.download_mbps is not None else 0.0,
                    'upload_mbps': float(metric.upload_mbps) if metric.upload_mbps is not None else 0.0,
                    'ping_ms': float(metric.ping_ms) if metric.ping_ms is not None else 0.0,
                    'packet_loss_percent': float(metric.packet_loss_percent) if metric.packet_loss_percent is not None else 0.0
                })
                
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error fetching performance data: {e}")
            return []
        finally:
            session.close()
            
    def get_weather_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get weather data for correlation analysis.
        
        Args:
            start_date: Start date for weather data
            end_date: End date for weather data
            
        Returns:
            List of weather data records
        """
        session = get_db_session()
        try:
            # Query weather data within the date range
            weather_records = session.query(WeatherData).filter(
                WeatherData.timestamp >= start_date,
                WeatherData.timestamp <= end_date
            ).order_by(WeatherData.timestamp).all()
            
            # Convert to dictionary format
            weather_data = []
            for record in weather_records:
                weather_data.append({
                    'timestamp': record.timestamp,
                    'temperature_2m': float(record.temperature_2m) if record.temperature_2m is not None else None,
                    'precipitation': float(record.precipitation) if record.precipitation is not None else None,
                    'wind_speed_10m': float(record.wind_speed_10m) if record.wind_speed_10m is not None else None,
                    'cloud_cover': float(record.cloud_cover) if record.cloud_cover is not None else None,
                    'pressure_msl': float(record.pressure_msl) if record.pressure_msl is not None else None,
                    'humidity_2m': float(record.humidity_2m) if record.humidity_2m is not None else None
                })
                
            return weather_data
            
        except Exception as e:
            self.logger.error(f"Error fetching weather data: {e}")
            return []
        finally:
            session.close()
            
    def analyze_correlations(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze correlations between weather and performance data.
        
        Args:
            days: Number of days to analyze (default: 7)
            
        Returns:
            Dictionary with correlation analysis results
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get performance and weather data
            performance_data = self.get_performance_data(start_date, end_date)
            weather_data = self.get_weather_data(start_date, end_date)
            
            if not performance_data or not weather_data:
                self.logger.warning("Insufficient data for correlation analysis")
                return {}
                
            self.logger.info(f"Analyzing correlations for {len(performance_data)} performance records and {len(weather_data)} weather records")
            
            # Perform correlation analysis
            correlations = self._calculate_correlations(weather_data, performance_data)
            
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                },
                'data_points': {
                    'performance': len(performance_data),
                    'weather': len(weather_data)
                },
                'correlations': correlations
            }
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}")
            return {}
            
    def _calculate_correlations(self, weather_data: List[Dict[str, Any]], performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate correlations between weather and performance parameters.
        
        Args:
            weather_data: List of weather data records
            performance_data: List of performance data records
            
        Returns:
            Dictionary with correlation results
        """
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            self.logger.warning("Pandas not available for correlation analysis")
            return {}
            
        try:
            # Convert to DataFrames
            weather_df = pd.DataFrame(weather_data)
            performance_df = pd.DataFrame(performance_data)
            
            # Ensure timestamp is datetime
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            performance_df['timestamp'] = pd.to_datetime(performance_df['timestamp'])
            
            # Merge dataframes on timestamp (nearest match within 1 hour)
            merged_df = pd.merge_asof(
                performance_df.sort_values('timestamp'),
                weather_df.sort_values('timestamp'),
                on='timestamp',
                direction='nearest',
                tolerance=pd.Timedelta('1H')
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
                            # Remove NaN values and calculate correlation
                            clean_data = merged_df[[weather_param, perf_param]].dropna()
                            if len(clean_data) > 1:
                                corr = clean_data[weather_param].corr(clean_data[perf_param])
                                correlations[weather_param][perf_param] = float(corr) if not pd.isna(corr) else 0.0
                            else:
                                correlations[weather_param][perf_param] = 0.0
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error calculating correlations: {e}")
            return {}
            
    def generate_correlation_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate a detailed correlation report.
        
        Args:
            days: Number of days to analyze (default: 7)
            
        Returns:
            Dictionary with detailed correlation report
        """
        analysis = self.analyze_correlations(days)
        
        if not analysis:
            return {}
            
        # Add interpretation to correlations
        interpreted_correlations = {}
        correlations = analysis.get('correlations', {})
        
        for weather_param, perf_correlations in correlations.items():
            interpreted_correlations[weather_param] = {}
            for perf_param, correlation_value in perf_correlations.items():
                # Interpret correlation strength
                abs_corr = abs(correlation_value)
                if abs_corr >= 0.7:
                    strength = "Strong"
                elif abs_corr >= 0.5:
                    strength = "Moderate"
                elif abs_corr >= 0.3:
                    strength = "Weak"
                else:
                    strength = "Very Weak"
                    
                # Determine relationship direction
                direction = "Positive" if correlation_value > 0 else "Negative" if correlation_value < 0 else "None"
                
                interpreted_correlations[weather_param][perf_param] = {
                    'correlation': correlation_value,
                    'strength': strength,
                    'direction': direction,
                    'interpretation': f"{strength} {direction.lower()} correlation"
                }
        
        analysis['interpreted_correlations'] = interpreted_correlations
        return analysis


def main():
    """Main entry point for weather-performance correlation analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Weather-Performance Correlation Analysis')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = WeatherPerformanceAnalyzer(args.config)
    
    # Generate correlation report
    report = analyzer.generate_correlation_report(args.days)
    
    if report:
        print(f"Correlation Analysis Report ({args.days} days)")
        print("=" * 50)
        print(f"Period: {report['period']['start']} to {report['period']['end']}")
        print(f"Data Points - Performance: {report['data_points']['performance']}, Weather: {report['data_points']['weather']}")
        print()
        
        # Display correlations
        correlations = report.get('interpreted_correlations', {})
        if correlations:
            print("Correlations:")
            for weather_param, perf_correlations in correlations.items():
                print(f"  {weather_param}:")
                for perf_param, details in perf_correlations.items():
                    print(f"    {perf_param}: {details['correlation']:.3f} ({details['interpretation']})")
        else:
            print("No correlations calculated")
    else:
        print("Failed to generate correlation report")


if __name__ == "__main__":
    main()