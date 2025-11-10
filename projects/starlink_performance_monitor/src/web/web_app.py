#!/usr/bin/env python3
"""
Starlink Performance Monitor Web Dashboard
Web interface for visualizing performance metrics.
"""

import json
import argparse
import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from functools import wraps

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_manager import get_database_manager, get_db_session

# Add project root to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logging, get_logger

# Add the src directory to the path so we can import from monitor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.monitor.monitor import PerformanceMetric, Base

# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

# Create Flask app with template folder specified
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app, cors_allowed_origins="*")

# Add secret key for sessions
app.secret_key = os.urandom(24)

def require_auth(f):
    """Decorator to require authentication for routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        web_app = WebApp(app.config.get('CONFIG_PATH', 'config.json'))
        if not web_app.is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        web_app = WebApp(app.config.get('CONFIG_PATH', 'config.json'))
        if web_app.authenticate_user(username, password):
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route."""
    session.pop('authenticated', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard page."""
    return render_template('enhanced_dashboard.html')

@app.route('/api/metrics')
@require_auth
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
@require_auth
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
            'packet_loss_percent': latest['packet_loss_percent'],  # Added packet loss
            'timestamp': latest['timestamp']
        }
    })

@app.route('/performance')
@require_auth
def performance():
    """Performance history page."""
    return render_template('performance.html')

@app.route('/alerts')
@require_auth
def alerts():
    """Alerts page."""
    return render_template('alerts.html')

@app.route('/reports')
@require_auth
def reports():
    """Reports page."""
    return render_template('reports.html')

@app.route('/settings')
@require_auth
def settings():
    """Settings page."""
    return render_template('settings.html')

class WebApp:
    """Web application for displaying performance metrics"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the web app with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db_manager = get_database_manager(config_path)
        self.db_engine = self.db_manager.get_engine()
        self.secret_key = self.config.get('web', {}).get('secret_key', os.urandom(24))
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _setup_database(self):
        """Setup database connection."""
        # This method is now handled by the database manager
        return self.db_manager.get_engine()
        
    def get_recent_metrics(self, hours: int = 24) -> pd.DataFrame:
        """
        Get recent performance metrics.
        
        Args:
            hours: Number of hours of data to retrieve
            
        Returns:
            DataFrame with recent metrics
        """
        session = get_db_session()
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
                'packet_loss_percent': m.packet_loss_percent,  # Added packet loss
                'server_name': m.server_name
            } for m in metrics]
            
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error retrieving metrics from database: {e}")
            return pd.DataFrame()
        finally:
            session.close()
            
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user based on username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            True if authentication is successful, False otherwise
        """
        web_config = self.config.get('web', {})
        auth_config = web_config.get('auth', {})
        
        if not auth_config.get('enabled', False):
            return True
            
        users = auth_config.get('users', [])
        for user in users:
            if user.get('username') == username:
                # Hash the provided password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if user.get('password_hash') == hashed_password:
                    return True
        return False
        
    def is_authenticated(self) -> bool:
        """Check if the current user is authenticated."""
        web_config = self.config.get('web', {})
        auth_config = web_config.get('auth', {})
        
        if not auth_config.get('enabled', False):
            return True
            
        return session.get('authenticated', False)

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
    
    # Run the application with SocketIO
    socketio.run(app, host=args.host, port=args.port, debug=args.debug)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('status', {'msg': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle real-time metrics request from client."""
    try:
        web_app = WebApp()
        df = web_app.get_recent_metrics(1)  # Last hour
        
        if not df.empty:
            latest = df.iloc[0]
            metrics = {
                'download_mbps': latest['download_mbps'],
                'upload_mbps': latest['upload_mbps'],
                'ping_ms': latest['ping_ms'],
                'packet_loss_percent': latest['packet_loss_percent'],
                'timestamp': latest['timestamp']
            }
            emit('metrics_update', metrics)
    except Exception as e:
        logger.error(f"Error handling metrics request: {e}")

if __name__ == "__main__":
    main()