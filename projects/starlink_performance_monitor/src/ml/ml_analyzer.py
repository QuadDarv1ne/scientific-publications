#!/usr/bin/env python3
"""
Starlink Performance Monitor
Main ML module that combines anomaly detection and performance forecasting.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import get_logger
from src.ml.anomaly_detection import AnomalyDetector
from src.ml.forecasting import PerformanceForecaster


class MLAnalyzer:
    """Main ML analyzer that combines anomaly detection and forecasting."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the ML analyzer with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.anomaly_detector = AnomalyDetector(config_path)
        self.forecaster = PerformanceForecaster(config_path)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def analyze_performance(self, anomaly_days: int = 30, forecast_days: int = 90, 
                          prediction_days: int = 7) -> Dict[str, Any]:
        """
        Perform complete performance analysis including anomaly detection and forecasting.
        
        Args:
            anomaly_days: Number of days for anomaly detection
            forecast_days: Number of days of historical data for forecasting
            prediction_days: Number of days to forecast
            
        Returns:
            Dictionary with complete analysis results
        """
        try:
            self.logger.info("Starting complete performance analysis")
            
            # Detect anomalies
            anomalies = self.anomaly_detector.detect_anomalies(anomaly_days)
            
            # Forecast performance
            forecasts = self.forecaster.forecast_performance(forecast_days, prediction_days)
            
            # Combine results
            analysis = {
                'timestamp': datetime.utcnow().isoformat(),
                'anomaly_detection': anomalies,
                'performance_forecasting': forecasts
            }
            
            self.logger.info("Performance analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return {}
            
    def generate_report(self, anomaly_days: int = 30, forecast_days: int = 90, 
                       prediction_days: int = 7) -> Dict[str, Any]:
        """
        Generate a comprehensive ML analysis report.
        
        Args:
            anomaly_days: Number of days for anomaly detection
            forecast_days: Number of days of historical data for forecasting
            prediction_days: Number of days to forecast
            
        Returns:
            Dictionary with analysis report
        """
        try:
            # Perform analysis
            analysis = self.analyze_performance(anomaly_days, forecast_days, prediction_days)
            
            if not analysis:
                return {}
                
            # Generate summary report
            report = {
                'generated_at': analysis['timestamp'],
                'summary': {}
            }
            
            # Add anomaly detection summary
            if 'anomaly_detection' in analysis and analysis['anomaly_detection']:
                anomaly_summary = {}
                for method_name, method_results in analysis['anomaly_detection']['methods'].items():
                    if method_results:
                        anomaly_summary[method_name] = {
                            'total_anomalies': method_results['anomaly_count'],
                            'anomaly_percentage': method_results['anomaly_percentage']
                        }
                report['summary']['anomaly_detection'] = anomaly_summary
                
            # Add forecasting summary
            if 'performance_forecasting' in analysis and analysis['performance_forecasting']:
                forecast_summary = {}
                for metric, forecasts in analysis['performance_forecasting']['forecasts'].items():
                    forecast_summary[metric] = {}
                    for method_name, method_results in forecasts.items():
                        if method_results:
                            forecast_summary[metric][method_name] = {
                                'forecast_count': len(method_results.get('forecasts', []))
                            }
                report['summary']['performance_forecasting'] = forecast_summary
                
            # Add full analysis data
            report['full_analysis'] = analysis
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating analysis report: {e}")
            return {}


def main():
    """Main entry point for ML analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor ML Analysis')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--anomaly-days', type=int, default=30, help='Number of days for anomaly detection')
    parser.add_argument('--forecast-days', type=int, default=90, help='Number of days of historical data for forecasting')
    parser.add_argument('--prediction-days', type=int, default=7, help='Number of days to forecast')
    parser.add_argument('--output', help='Output file for report (JSON format)')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = MLAnalyzer(args.config)
    
    # Generate report
    report = analyzer.generate_report(args.anomaly_days, args.forecast_days, args.prediction_days)
    
    if report:
        print("ML Performance Analysis Report")
        print("=" * 50)
        print(f"Generated at: {report['generated_at']}")
        print()
        
        # Display summary
        if 'anomaly_detection' in report['summary']:
            print("Anomaly Detection Summary:")
            for method_name, summary in report['summary']['anomaly_detection'].items():
                print(f"  {method_name.replace('_', ' ').title()}: "
                      f"{summary['total_anomalies']} anomalies ({summary['anomaly_percentage']:.2f}%)")
            print()
            
        if 'performance_forecasting' in report['summary']:
            print("Performance Forecasting Summary:")
            for metric, forecasts in report['summary']['performance_forecasting'].items():
                print(f"  {metric.replace('_', ' ').title()}:")
                for method_name, summary in forecasts.items():
                    print(f"    {method_name.replace('_', ' ').title()}: "
                          f"{summary['forecast_count']} day forecast")
            print()
            
        # Save to file if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to {args.output}")
    else:
        print("Failed to generate ML analysis report")


if __name__ == "__main__":
    main()