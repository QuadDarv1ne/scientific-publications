#!/usr/bin/env python3
"""
Starlink Performance Monitor
Machine Learning module for anomaly detection in performance metrics.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.covariance import EllipticEnvelope
from sqlalchemy import and_

from src.utils.logging_config import get_logger
from src.database.db_manager import get_db_session
from src.database.models import PerformanceMetric


class AnomalyDetector:
    """Detect anomalies in performance metrics using machine learning."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the anomaly detector with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.ml_config = self.config.get('ml', {}).get('anomaly_detection', {})
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def get_performance_data(self, days: int = 30) -> pd.DataFrame:
        """
        Get performance data for anomaly detection.
        
        Args:
            days: Number of days of historical data to retrieve
            
        Returns:
            DataFrame with performance metrics
        """
        session = get_db_session()
        try:
            # Calculate date threshold
            threshold = datetime.utcnow() - timedelta(days=days)
            
            # Query performance metrics
            metrics = session.query(PerformanceMetric).filter(
                PerformanceMetric.timestamp >= threshold
            ).order_by(PerformanceMetric.timestamp).all()
            
            # Convert to DataFrame
            data = []
            for metric in metrics:
                data.append({
                    'timestamp': metric.timestamp,
                    'download_mbps': float(metric.download_mbps) if metric.download_mbps is not None else 0.0,
                    'upload_mbps': float(metric.upload_mbps) if metric.upload_mbps is not None else 0.0,
                    'ping_ms': float(metric.ping_ms) if metric.ping_ms is not None else 0.0,
                    'packet_loss_percent': float(metric.packet_loss_percent) if metric.packet_loss_percent is not None else 0.0
                })
                
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"Error fetching performance data: {e}")
            return pd.DataFrame()
        finally:
            session.close()
            
    def detect_anomalies_isolation_forest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies using Isolation Forest algorithm.
        
        Args:
            df: DataFrame with performance metrics
            
        Returns:
            Dictionary with anomaly detection results
        """
        if df.empty:
            return {}
            
        try:
            # Prepare data for anomaly detection
            feature_columns = ['download_mbps', 'upload_mbps', 'ping_ms', 'packet_loss_percent']
            X = df[feature_columns].values
            
            # Handle missing values
            X = np.nan_to_num(X, nan=0.0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Configure Isolation Forest
            contamination = self.ml_config.get('isolation_forest', {}).get('contamination', 0.1)
            random_state = self.ml_config.get('isolation_forest', {}).get('random_state', 42)
            
            # Create and fit the model
            iso_forest = IsolationForest(
                contamination=contamination,
                random_state=random_state,
                n_estimators=100
            )
            anomaly_labels = iso_forest.fit_predict(X_scaled)
            
            # Calculate anomaly scores
            anomaly_scores = iso_forest.decision_function(X_scaled)
            
            # Identify anomalies (label = -1)
            anomaly_indices = np.where(anomaly_labels == -1)[0]
            
            # Prepare results
            anomalies = []
            for idx in anomaly_indices:
                anomalies.append({
                    'timestamp': df.iloc[idx]['timestamp'],
                    'download_mbps': float(df.iloc[idx]['download_mbps']),
                    'upload_mbps': float(df.iloc[idx]['upload_mbps']),
                    'ping_ms': float(df.iloc[idx]['ping_ms']),
                    'packet_loss_percent': float(df.iloc[idx]['packet_loss_percent']),
                    'anomaly_score': float(anomaly_scores[idx])
                })
                
            self.logger.info(f"Detected {len(anomalies)} anomalies using Isolation Forest")
            
            return {
                'method': 'isolation_forest',
                'anomalies': anomalies,
                'total_points': len(df),
                'anomaly_count': len(anomalies),
                'anomaly_percentage': len(anomalies) / len(df) * 100 if len(df) > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error in Isolation Forest anomaly detection: {e}")
            return {}
            
    def detect_anomalies_dbscan(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies using DBSCAN clustering algorithm.
        
        Args:
            df: DataFrame with performance metrics
            
        Returns:
            Dictionary with anomaly detection results
        """
        if df.empty:
            return {}
            
        try:
            # Prepare data for anomaly detection
            feature_columns = ['download_mbps', 'upload_mbps', 'ping_ms', 'packet_loss_percent']
            X = df[feature_columns].values
            
            # Handle missing values
            X = np.nan_to_num(X, nan=0.0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Configure DBSCAN
            eps = self.ml_config.get('dbscan', {}).get('eps', 0.5)
            min_samples = self.ml_config.get('dbscan', {}).get('min_samples', 5)
            
            # Create and fit the model
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = dbscan.fit_predict(X_scaled)
            
            # Identify noise points (label = -1) as anomalies
            anomaly_indices = np.where(cluster_labels == -1)[0]
            
            # Prepare results
            anomalies = []
            for idx in anomaly_indices:
                anomalies.append({
                    'timestamp': df.iloc[idx]['timestamp'],
                    'download_mbps': float(df.iloc[idx]['download_mbps']),
                    'upload_mbps': float(df.iloc[idx]['upload_mbps']),
                    'ping_ms': float(df.iloc[idx]['ping_ms']),
                    'packet_loss_percent': float(df.iloc[idx]['packet_loss_percent'])
                })
                
            self.logger.info(f"Detected {len(anomalies)} anomalies using DBSCAN")
            
            return {
                'method': 'dbscan',
                'anomalies': anomalies,
                'total_points': len(df),
                'anomaly_count': len(anomalies),
                'anomaly_percentage': len(anomalies) / len(df) * 100 if len(df) > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error in DBSCAN anomaly detection: {e}")
            return {}
            
    def detect_anomalies_elliptic_envelope(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies using Elliptic Envelope algorithm.
        
        Args:
            df: DataFrame with performance metrics
            
        Returns:
            Dictionary with anomaly detection results
        """
        if df.empty:
            return {}
            
        try:
            # Prepare data for anomaly detection
            feature_columns = ['download_mbps', 'upload_mbps', 'ping_ms', 'packet_loss_percent']
            X = df[feature_columns].values
            
            # Handle missing values
            X = np.nan_to_num(X, nan=0.0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Configure Elliptic Envelope
            contamination = self.ml_config.get('elliptic_envelope', {}).get('contamination', 0.1)
            random_state = self.ml_config.get('elliptic_envelope', {}).get('random_state', 42)
            
            # Create and fit the model
            elliptic_env = EllipticEnvelope(
                contamination=contamination,
                random_state=random_state
            )
            anomaly_labels = elliptic_env.fit_predict(X_scaled)
            
            # Identify anomalies (label = -1)
            anomaly_indices = np.where(anomaly_labels == -1)[0]
            
            # Prepare results
            anomalies = []
            for idx in anomaly_indices:
                anomalies.append({
                    'timestamp': df.iloc[idx]['timestamp'],
                    'download_mbps': float(df.iloc[idx]['download_mbps']),
                    'upload_mbps': float(df.iloc[idx]['upload_mbps']),
                    'ping_ms': float(df.iloc[idx]['ping_ms']),
                    'packet_loss_percent': float(df.iloc[idx]['packet_loss_percent'])
                })
                
            self.logger.info(f"Detected {len(anomalies)} anomalies using Elliptic Envelope")
            
            return {
                'method': 'elliptic_envelope',
                'anomalies': anomalies,
                'total_points': len(df),
                'anomaly_count': len(anomalies),
                'anomaly_percentage': len(anomalies) / len(df) * 100 if len(df) > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error in Elliptic Envelope anomaly detection: {e}")
            return {}
            
    def detect_anomalies(self, days: int = 30) -> Dict[str, Any]:
        """
        Detect anomalies using multiple algorithms and combine results.
        
        Args:
            days: Number of days of historical data to analyze
            
        Returns:
            Dictionary with combined anomaly detection results
        """
        try:
            # Get performance data
            df = self.get_performance_data(days)
            
            if df.empty:
                self.logger.warning("No performance data available for anomaly detection")
                return {}
                
            self.logger.info(f"Analyzing {len(df)} data points for anomalies")
            
            # Run multiple anomaly detection algorithms
            iso_forest_results = self.detect_anomalies_isolation_forest(df)
            dbscan_results = self.detect_anomalies_dbscan(df)
            elliptic_env_results = self.detect_anomalies_elliptic_envelope(df)
            
            # Combine results
            all_results = {
                'period': {
                    'start': df['timestamp'].min().isoformat() if not df.empty else None,
                    'end': df['timestamp'].max().isoformat() if not df.empty else None,
                    'days': days
                },
                'methods': {
                    'isolation_forest': iso_forest_results,
                    'dbscan': dbscan_results,
                    'elliptic_envelope': elliptic_env_results
                }
            }
            
            return all_results
            
        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {e}")
            return {}


def main():
    """Main entry point for anomaly detection."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Anomaly Detection')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = AnomalyDetector(args.config)
    
    # Detect anomalies
    results = detector.detect_anomalies(args.days)
    
    if results:
        print(f"Anomaly Detection Report ({args.days} days)")
        print("=" * 50)
        print(f"Period: {results['period']['start']} to {results['period']['end']}")
        print()
        
        # Display results for each method
        for method_name, method_results in results['methods'].items():
            if method_results:
                print(f"{method_name.replace('_', ' ').title()}:")
                print(f"  Total anomalies: {method_results['anomaly_count']}")
                print(f"  Anomaly percentage: {method_results['anomaly_percentage']:.2f}%")
                print(f"  Anomalies:")
                for anomaly in method_results['anomalies'][:5]:  # Show first 5 anomalies
                    print(f"    {anomaly['timestamp']}: "
                          f"Download={anomaly['download_mbps']:.2f} Mbps, "
                          f"Upload={anomaly['upload_mbps']:.2f} Mbps, "
                          f"Ping={anomaly['ping_ms']:.2f} ms, "
                          f"Packet Loss={anomaly['packet_loss_percent']:.2f}%")
                if len(method_results['anomalies']) > 5:
                    print(f"    ... and {len(method_results['anomalies']) - 5} more")
                print()
    else:
        print("Failed to detect anomalies")


if __name__ == "__main__":
    main()