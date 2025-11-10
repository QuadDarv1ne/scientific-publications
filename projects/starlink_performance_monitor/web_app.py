#!/usr/bin/env python3
"""
Starlink Performance Monitor Web Dashboard
Web interface for visualizing performance metrics.
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from monitor import PerformanceMetric, Base

app = Flask(__name__)

class WebApp:
    """Web application for displaying performance metrics"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the web app with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db_engine = self._setup_database()
        self.db_session = sessionmaker(bind=self.db_engine)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _setup_database(self):
        """Setup database connection."""
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'postgresql':
            db_url = f"postgresql://{db_config.get('user', 'user')}:{db_config.get('password', 'password')}@" \
                     f"{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('name', 'starlink_monitor')}"
        else:
            db_url = "sqlite:///starlink_monitor.db"
            
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        return engine
        
    def get_recent_metrics(self, hours: int = 24) -> pd.DataFrame:
        """
        Get recent performance metrics.
        
        Args:
            hours: Number of hours of data to retrieve
            
        Returns:
            DataFrame with recent metrics
        """
        session = self.db_session()
        try:
            # Calculate time threshold
            threshold = datetime.utcnow() - timedelta(hours=hours)
            
            # Query recent metrics
            metrics = session.query(PerformanceMetric).filter(
                PerformanceMetric.timestamp >= threshold
            ).order_by(desc(PerformanceMetric.timestamp)).all()
            
            # Convert to DataFrame
            data = [{
                'timestamp': m.timestamp,
                'download_mbps': m.download_mbps,
                'upload_mbps': m.upload_mbps,
                'ping_ms': m.ping_ms,
                'server_name': m.server_name
            } for m in metrics]
            
            return pd.DataFrame(data)
        finally:
            session.close()

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for performance metrics."""
    hours = int(request.args.get('hours', 24))
    
    web_app = WebApp()
    df = web_app.get_recent_metrics(hours)
    
    if df.empty:
        return jsonify({'data': []})
    
    # Convert to JSON-serializable format
    df['timestamp'] = df['timestamp'].astype(str)
    return jsonify({'data': df.to_dict(orient='records')})

@app.route('/api/current')
def api_current():
    """API endpoint for current metrics."""
    web_app = WebApp()
    df = web_app.get_recent_metrics(1)  # Last hour
    
    if df.empty:
        return jsonify({'metrics': None})
    
    # Get latest metrics
    latest = df.iloc[0]
    return jsonify({
        'metrics': {
            'download_mbps': latest['download_mbps'],
            'upload_mbps': latest['upload_mbps'],
            'ping_ms': latest['ping_ms'],
            'timestamp': latest['timestamp']
        }
    })

@app.route('/performance')
def performance():
    """Performance history page."""
    return render_template('performance.html')

@app.route('/alerts')
def alerts():
    """Alerts page."""
    return render_template('alerts.html')

@app.route('/reports')
def reports():
    """Reports page."""
    return render_template('reports.html')

@app.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')

def main():
    """Main entry point for the web application."""
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Web Dashboard')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8050, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Update app configuration
    app.config['CONFIG_PATH'] = args.config
    
    # Run the application
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()