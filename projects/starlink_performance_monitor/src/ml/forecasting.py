#!/usr/bin/env python3
"""
Starlink Performance Monitor
Machine Learning module for performance forecasting.
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
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from sqlalchemy import and_

from src.utils.logging_config import get_logger
from src.database.db_manager import get_db_session
from src.database.models import PerformanceMetric


class PerformanceForecaster:
    """Forecast performance metrics using machine learning."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the performance forecaster with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.ml_config = self.config.get('ml', {}).get('forecasting', {})
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def get_performance_data(self, days: int = 90) -> pd.DataFrame:
        """
        Get performance data for forecasting.
        
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
                
            df = pd.DataFrame(data)
            
            # Set timestamp as index for time series analysis
            if not df.empty:
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching performance data: {e}")
            return pd.DataFrame()
        finally:
            session.close()
            
    def prepare_features(self, df: pd.DataFrame, target_column: str, lookback_days: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for machine learning models.
        
        Args:
            df: DataFrame with performance metrics
            target_column: Column to predict
            lookback_days: Number of days to look back for features
            
        Returns:
            Tuple of (features, targets)
        """
        if df.empty or target_column not in df.columns:
            return np.array([]), np.array([])
            
        # Create lagged features
        features = []
        targets = []
        
        # Use multiple lagged values as features
        for i in range(lookback_days, len(df)):
            # Target value
            target = df[target_column].iloc[i]
            
            # Feature values (previous days)
            feature_row = []
            for j in range(1, lookback_days + 1):
                if i - j >= 0:
                    feature_row.append(df[target_column].iloc[i - j])
                else:
                    feature_row.append(0.0)
                    
            # Add other metrics from the same day as additional features
            if i < len(df):
                feature_row.extend([
                    df['download_mbps'].iloc[i],
                    df['upload_mbps'].iloc[i],
                    df['ping_ms'].iloc[i],
                    df['packet_loss_percent'].iloc[i]
                ])
                
            features.append(feature_row)
            targets.append(target)
            
        return np.array(features), np.array(targets)
        
    def forecast_linear_regression(self, df: pd.DataFrame, target_column: str, 
                                 forecast_days: int = 7) -> Dict[str, Any]:
        """
        Forecast using Linear Regression.
        
        Args:
            df: DataFrame with performance metrics
            target_column: Column to predict
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        if df.empty or target_column not in df.columns:
            return {}
            
        try:
            # Prepare features
            lookback_days = self.ml_config.get('linear_regression', {}).get('lookback_days', 7)
            X, y = self.prepare_features(df, target_column, lookback_days)
            
            if len(X) == 0 or len(y) == 0:
                return {}
                
            # Split data for training and validation
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Validate model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Forecast future values
            forecasts = []
            current_features = X[-1].copy()  # Start with last known features
            
            for i in range(forecast_days):
                # Predict next value
                next_value = model.predict([current_features])[0]
                forecasts.append(float(next_value))
                
                # Update features for next prediction
                # Shift features and add new prediction
                current_features = np.roll(current_features, -1)
                current_features[-1] = next_value
                
            self.logger.info(f"Linear Regression forecast for {target_column}: {len(forecasts)} days")
            
            return {
                'method': 'linear_regression',
                'target': target_column,
                'forecasts': forecasts,
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in Linear Regression forecasting for {target_column}: {e}")
            return {}
            
    def forecast_random_forest(self, df: pd.DataFrame, target_column: str, 
                              forecast_days: int = 7) -> Dict[str, Any]:
        """
        Forecast using Random Forest.
        
        Args:
            df: DataFrame with performance metrics
            target_column: Column to predict
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        if df.empty or target_column not in df.columns:
            return {}
            
        try:
            # Prepare features
            lookback_days = self.ml_config.get('random_forest', {}).get('lookback_days', 7)
            X, y = self.prepare_features(df, target_column, lookback_days)
            
            if len(X) == 0 or len(y) == 0:
                return {}
                
            # Split data for training and validation
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train model
            n_estimators = self.ml_config.get('random_forest', {}).get('n_estimators', 100)
            random_state = self.ml_config.get('random_forest', {}).get('random_state', 42)
            
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
            model.fit(X_train, y_train)
            
            # Validate model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Forecast future values
            forecasts = []
            current_features = X[-1].copy()  # Start with last known features
            
            for i in range(forecast_days):
                # Predict next value
                next_value = model.predict([current_features])[0]
                forecasts.append(float(next_value))
                
                # Update features for next prediction
                # Shift features and add new prediction
                current_features = np.roll(current_features, -1)
                current_features[-1] = next_value
                
            self.logger.info(f"Random Forest forecast for {target_column}: {len(forecasts)} days")
            
            return {
                'method': 'random_forest',
                'target': target_column,
                'forecasts': forecasts,
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in Random Forest forecasting for {target_column}: {e}")
            return {}
            
    def forecast_arima(self, df: pd.DataFrame, target_column: str, 
                      forecast_days: int = 7) -> Dict[str, Any]:
        """
        Forecast using ARIMA model.
        
        Args:
            df: DataFrame with performance metrics
            target_column: Column to predict
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        if df.empty or target_column not in df.columns:
            return {}
            
        try:
            # Prepare time series data
            ts_data = df[target_column].dropna()
            
            if len(ts_data) < 10:  # Need minimum data points
                return {}
                
            # Fit ARIMA model
            order = self.ml_config.get('arima', {}).get('order', (1, 1, 1))
            model = ARIMA(ts_data, order=order)
            fitted_model = model.fit()
            
            # Forecast
            forecast_result = fitted_model.forecast(steps=forecast_days)
            forecasts = [float(x) for x in forecast_result]
            
            # Get confidence intervals
            try:
                forecast_ci = fitted_model.get_forecast(steps=forecast_days)
                conf_int = forecast_ci.conf_int()
                lower_bounds = [float(x) for x in conf_int.iloc[:, 0]]
                upper_bounds = [float(x) for x in conf_int.iloc[:, 1]]
            except:
                lower_bounds = [0.0] * forecast_days
                upper_bounds = [0.0] * forecast_days
            
            self.logger.info(f"ARIMA forecast for {target_column}: {len(forecasts)} days")
            
            return {
                'method': 'arima',
                'target': target_column,
                'forecasts': forecasts,
                'confidence_intervals': {
                    'lower': lower_bounds,
                    'upper': upper_bounds
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in ARIMA forecasting for {target_column}: {e}")
            return {}
            
    def forecast_performance(self, days: int = 90, forecast_days: int = 7) -> Dict[str, Any]:
        """
        Forecast performance metrics using multiple algorithms.
        
        Args:
            days: Number of days of historical data to use
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with combined forecast results
        """
        try:
            # Get performance data
            df = self.get_performance_data(days)
            
            if df.empty:
                self.logger.warning("No performance data available for forecasting")
                return {}
                
            self.logger.info(f"Forecasting performance for {forecast_days} days using {len(df)} historical data points")
            
            # Forecast each metric
            metrics_to_forecast = ['download_mbps', 'upload_mbps', 'ping_ms', 'packet_loss_percent']
            forecasts = {}
            
            for metric in metrics_to_forecast:
                if metric in df.columns:
                    # Run multiple forecasting algorithms
                    lr_forecast = self.forecast_linear_regression(df, metric, forecast_days)
                    rf_forecast = self.forecast_random_forest(df, metric, forecast_days)
                    arima_forecast = self.forecast_arima(df, metric, forecast_days)
                    
                    forecasts[metric] = {
                        'linear_regression': lr_forecast,
                        'random_forest': rf_forecast,
                        'arima': arima_forecast
                    }
            
            # Combine results
            results = {
                'period': {
                    'historical_start': df.index.min().isoformat() if not df.empty else None,
                    'historical_end': df.index.max().isoformat() if not df.empty else None,
                    'forecast_start': (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    'forecast_end': (datetime.utcnow() + timedelta(days=forecast_days)).isoformat(),
                    'historical_days': days,
                    'forecast_days': forecast_days
                },
                'forecasts': forecasts
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in performance forecasting: {e}")
            return {}


def main():
    """Main entry point for performance forecasting."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Performance Forecasting')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--days', type=int, default=90, help='Number of days of historical data to use')
    parser.add_argument('--forecast-days', type=int, default=7, help='Number of days to forecast')
    
    args = parser.parse_args()
    
    # Initialize forecaster
    forecaster = PerformanceForecaster(args.config)
    
    # Forecast performance
    results = forecaster.forecast_performance(args.days, args.forecast_days)
    
    if results:
        print(f"Performance Forecast Report")
        print("=" * 50)
        print(f"Historical period: {results['period']['historical_start']} to {results['period']['historical_end']}")
        print(f"Forecast period: {results['period']['forecast_start']} to {results['period']['forecast_end']}")
        print()
        
        # Display forecasts for each metric
        for metric, forecasts in results['forecasts'].items():
            print(f"{metric.replace('_', ' ').title()} Forecasts:")
            for method_name, method_results in forecasts.items():
                if method_results:
                    print(f"  {method_name.replace('_', ' ').title()}:")
                    if 'forecasts' in method_results:
                        for i, forecast in enumerate(method_results['forecasts'][:3]):  # Show first 3 forecasts
                            forecast_date = datetime.utcnow() + timedelta(days=i+1)
                            print(f"    {forecast_date.strftime('%Y-%m-%d')}: {forecast:.2f}")
                        if len(method_results['forecasts']) > 3:
                            print(f"    ... and {len(method_results['forecasts']) - 3} more days")
            print()
    else:
        print("Failed to generate performance forecasts")


if __name__ == "__main__":
    main()