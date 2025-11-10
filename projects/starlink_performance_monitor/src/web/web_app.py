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
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import these first before other imports that might depend on them
from src.database.db_manager import get_database_manager, get_db_session
from src.utils.logging_config import setup_logging, get_logger

# Add project root to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import after the initial setup
from src.monitor.monitor import PerformanceMetric, Base
from src.web.realtime_manager import start_realtime_updater, stop_realtime_updater

# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

# Language translations dictionary
LANGUAGES = {
    'en': {
        'dashboard': 'Dashboard',
        'performance': 'Performance',
        'alerts': 'Alerts',
        'reports': 'Reports',
        'settings': 'Settings',
        'ml_analysis': 'ML Analysis',
        'logout': 'Logout',
        'login': 'Login',
        'username': 'Username',
        'password': 'Password',
        'invalid_credentials': 'Invalid credentials',
        'performance_history': 'Performance History',
        'alerts_notifications': 'Alerts & Notifications',
        'last_1_hour': 'Last 1 Hour',
        'last_6_hours': 'Last 6 Hours',
        'last_12_hours': 'Last 12 Hours',
        'last_24_hours': 'Last 24 Hours',
        'last_7_days': 'Last 7 Days',
        'download_speed': 'Download Speed',
        'upload_speed': 'Upload Speed',
        'ping': 'Ping',
        'packet_loss': 'Packet Loss',
        'performance_history_chart': 'Performance History',
        'download_distribution': 'Download Speed Distribution',
        'ping_performance': 'Ping Performance',
        'packet_loss_over_time': 'Packet Loss Over Time',
        'performance_summary': 'Performance Summary',
        'weather_correlation_analysis': 'Weather Correlation Analysis',
        'weather_parameter': 'Weather Parameter',
        'performance_metric': 'Performance Metric',
        'correlation': 'Correlation',
        'strength': 'Strength',
        'interpretation': 'Interpretation',
        'recent_alerts': 'Recent Alerts',
        'time': 'Time',
        'type': 'Type',
        'message': 'Message',
        'value': 'Value',
        'threshold': 'Threshold',
        'no_correlation_data': 'No correlation data available',
        'no_recent_alerts': 'No recent alerts',
        'error_loading_data': 'Error loading data',
        'refresh': 'Refresh',
        'auto_refresh': 'Auto Refresh',
        'line': 'Line',
        'bar': 'Bar',
        'area': 'Area',
        'connecting_data_stream': 'Connecting to real-time data stream...',
        'connected_data_stream': 'Connected to real-time data stream',
        'disconnected_data_stream': 'Disconnected from real-time data stream',
        'data_stream_simulation': 'Real-time data stream simulation active',
        'failed_connect_data_stream': 'Failed to connect to real-time data stream',
        'data_updated': 'Data updated successfully',
        'error_fetching_metrics': 'Error fetching current metrics',
        'no_data_time_range': 'No data available for the selected time range',
        'error_fetching_chart': 'Error fetching chart data',
        'site_name': 'Starlink Performance Monitor',
        'frequency': 'Frequency',
        'performance_metrics': 'Performance Metrics',
        'save_settings': 'Save Settings',
        'reset_defaults': 'Reset to Defaults',
        'general': 'General',
        'monitoring': 'Monitoring',
        'notifications': 'Notifications',
        'database': 'Database',
        'web_interface': 'Web Interface',
        'weather_integration': 'Weather Integration',
        'user_management': 'User Management',
        'general_settings': 'General Settings',
        'timezone': 'Timezone',
        'language': 'Language',
        'auto_update': 'Automatically check for updates',
        'monitoring_settings': 'Monitoring Settings',
        'monitoring_interval': 'Monitoring Interval (minutes)',
        'speed_test_config': 'Speed Test Configuration',
        'enable_speed_tests': 'Enable Speed Tests',
        'use_specific_servers': 'Use Specific Speed Test Servers',
        'server_ids': 'Server IDs (comma separated)',
        'ping_test_config': 'Ping Test Configuration',
        'enable_ping_tests': 'Enable Ping Tests',
        'server_name': 'Server Name',
        'ip_address': 'IP Address',
        'add_server': 'Add Server',
        'notification_settings': 'Notification Settings',
        'telegram_notifications': 'Telegram Notifications',
        'enable_telegram': 'Enable Telegram Notifications',
        'bot_token': 'Bot Token',
        'chat_id': 'Chat ID',
        'download_threshold': 'Download Threshold (Mbps)',
        'ping_threshold': 'Ping Threshold (ms)',
        'email_notifications': 'Email Notifications',
        'enable_email': 'Enable Email Notifications',
        'smtp_server': 'SMTP Server',
        'port': 'Port',
        'database_settings': 'Database Settings',
        'database_type': 'Database Type',
        'host': 'Host',
        'database_name': 'Database Name',
        'web_interface_settings': 'Web Interface Settings',
        'authentication': 'Authentication',
        'enable_authentication': 'Enable Authentication',
        'manage_users': 'Manage Users',
        'enable_debug_mode': 'Enable Debug Mode',
        'api_key': 'API Key',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'weather_parameters': 'Weather Parameters',
        'temperature': 'Temperature',
        'precipitation': 'Precipitation',
        'wind_speed': 'Wind Speed',
        'cloud_cover': 'Cloud Cover',
        'role': 'Role',
        'last_login': 'Last Login',
        'actions': 'Actions',
        'administrator': 'Administrator',
        'edit': 'Edit',
        'delete': 'Delete',
        'add_user': 'Add User',
        'add_new_user': 'Add New User',
        'enter_username': 'Enter username',
        'enter_password': 'Enter password',
        'user': 'User',
        'cancel': 'Cancel',
        'reset_confirmation': 'Are you sure you want to reset all settings to their default values? This action cannot be undone.',
        'confirm_reset': 'Yes, I want to reset all settings',
        'settings_saved': 'Settings saved successfully!',
        'settings_reset': 'Settings reset to defaults.',
        'enable_weather_integration': 'Enable Weather Integration',
        'navigation': 'Navigation',
        'minutes': 'minutes'
    },
    'ru': {
        'dashboard': 'Панель управления',
        'performance': 'Производительность',
        'alerts': 'Оповещения',
        'reports': 'Отчеты',
        'settings': 'Настройки',
        'ml_analysis': 'Анализ ML',
        'logout': 'Выйти',
        'login': 'Войти',
        'username': 'Имя пользователя',
        'password': 'Пароль',
        'invalid_credentials': 'Неверные учетные данные',
        'performance_history': 'История производительности',
        'alerts_notifications': 'Оповещения и уведомления',
        'last_1_hour': 'Последний 1 час',
        'last_6_hours': 'Последние 6 часов',
        'last_12_hours': 'Последние 12 часов',
        'last_24_hours': 'Последние 24 часа',
        'last_7_days': 'Последние 7 дней',
        'download_speed': 'Скорость загрузки',
        'upload_speed': 'Скорость отдачи',
        'ping': 'Пинг',
        'packet_loss': 'Потери пакетов',
        'performance_history_chart': 'История производительности',
        'download_distribution': 'Распределение скорости загрузки',
        'ping_performance': 'Производительность пинга',
        'packet_loss_over_time': 'Потери пакетов со временем',
        'performance_summary': 'Сводка производительности',
        'weather_correlation_analysis': 'Анализ корреляции погоды',
        'weather_parameter': 'Параметр погоды',
        'performance_metric': 'Метрика производительности',
        'correlation': 'Корреляция',
        'strength': 'Сила',
        'interpretation': 'Интерпретация',
        'recent_alerts': 'Последние оповещения',
        'time': 'Время',
        'type': 'Тип',
        'message': 'Сообщение',
        'value': 'Значение',
        'threshold': 'Порог',
        'no_correlation_data': 'Нет данных о корреляции',
        'no_recent_alerts': 'Нет последних оповещений',
        'error_loading_data': 'Ошибка загрузки данных',
        'refresh': 'Обновить',
        'auto_refresh': 'Автообновление',
        'line': 'Линия',
        'bar': 'Столбцы',
        'area': 'Область',
        'connecting_data_stream': 'Подключение к потоку данных в реальном времени...',
        'connected_data_stream': 'Подключено к потоку данных в реальном времени',
        'disconnected_data_stream': 'Отключено от потока данных в реальном времени',
        'data_stream_simulation': 'Симуляция потока данных в реальном времени активна',
        'failed_connect_data_stream': 'Не удалось подключиться к потоку данных в реальном времени',
        'data_updated': 'Данные успешно обновлены',
        'error_fetching_metrics': 'Ошибка получения текущих метрик',
        'no_data_time_range': 'Нет данных для выбранного временного диапазона',
        'error_fetching_chart': 'Ошибка получения данных диаграммы',
        'site_name': 'Монитор производительности Starlink',
        'frequency': 'Частота',
        'performance_metrics': 'Метрики производительности',
        'save_settings': 'Сохранить настройки',
        'reset_defaults': 'Сбросить к значениям по умолчанию',
        'general': 'Общие',
        'monitoring': 'Мониторинг',
        'notifications': 'Уведомления',
        'database': 'База данных',
        'web_interface': 'Веб-интерфейс',
        'weather_integration': 'Интеграция погоды',
        'user_management': 'Управление пользователями',
        'general_settings': 'Общие настройки',
        'timezone': 'Часовой пояс',
        'language': 'Язык',
        'auto_update': 'Автоматически проверять обновления',
        'monitoring_settings': 'Настройки мониторинга',
        'monitoring_interval': 'Интервал мониторинга (минуты)',
        'speed_test_config': 'Конфигурация теста скорости',
        'enable_speed_tests': 'Включить тесты скорости',
        'use_specific_servers': 'Использовать определенные серверы тестирования скорости',
        'server_ids': 'ID серверов (через запятую)',
        'ping_test_config': 'Конфигурация теста пинга',
        'enable_ping_tests': 'Включить тесты пинга',
        'server_name': 'Имя сервера',
        'ip_address': 'IP адрес',
        'add_server': 'Добавить сервер',
        'notification_settings': 'Настройки уведомлений',
        'telegram_notifications': 'Уведомления Telegram',
        'enable_telegram': 'Включить уведомления Telegram',
        'bot_token': 'Токен бота',
        'chat_id': 'ID чата',
        'download_threshold': 'Порог скорости загрузки (Мбит/с)',
        'ping_threshold': 'Порог пинга (мс)',
        'email_notifications': 'Уведомления по электронной почте',
        'enable_email': 'Включить уведомления по электронной почте',
        'smtp_server': 'SMTP сервер',
        'port': 'Порт',
        'database_settings': 'Настройки базы данных',
        'database_type': 'Тип базы данных',
        'host': 'Хост',
        'database_name': 'Имя базы данных',
        'web_interface_settings': 'Настройки веб-интерфейса',
        'authentication': 'Аутентификация',
        'enable_authentication': 'Включить аутентификацию',
        'manage_users': 'Управление пользователями',
        'enable_debug_mode': 'Включить режим отладки',
        'api_key': 'API ключ',
        'latitude': 'Широта',
        'longitude': 'Долгота',
        'weather_parameters': 'Параметры погоды',
        'temperature': 'Температура',
        'precipitation': 'Осадки',
        'wind_speed': 'Скорость ветра',
        'cloud_cover': 'Облачность',
        'role': 'Роль',
        'last_login': 'Последний вход',
        'actions': 'Действия',
        'administrator': 'Администратор',
        'edit': 'Редактировать',
        'delete': 'Удалить',
        'add_user': 'Добавить пользователя',
        'add_new_user': 'Добавить нового пользователя',
        'enter_username': 'Введите имя пользователя',
        'enter_password': 'Введите пароль',
        'user': 'Пользователь',
        'cancel': 'Отмена',
        'reset_confirmation': 'Вы уверены, что хотите сбросить все настройки к значениям по умолчанию? Это действие нельзя отменить.',
        'confirm_reset': 'Да, я хочу сбросить все настройки',
        'settings_saved': 'Настройки успешно сохранены!',
        'settings_reset': 'Настройки сброшены к значениям по умолчанию.',
        'enable_weather_integration': 'Включить интеграцию погоды',
        'navigation': 'Навигация',
        'minutes': 'минуты'
    }
}

# Create Flask app with template folder specified
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Add secret key for sessions
app.secret_key = os.urandom(24)

def get_translations():
    """Get translations for the current language."""
    lang = session.get('language', 'en')
    return LANGUAGES.get(lang, LANGUAGES['en'])

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

@app.context_processor
def inject_translations():
    """Inject translations into template context."""
    return dict(t=get_translations())

@app.route('/set_language/<lang>')
def set_language(lang):
    """Set the language for the session."""
    if lang in LANGUAGES:
        session['language'] = lang
    return redirect(request.referrer or url_for('dashboard'))

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
            return render_template('login.html', error='invalid_credentials')
    
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

@app.route('/ml-analysis')
@require_auth
def ml_analysis():
    """ML analysis page."""
    return render_template('ml_analysis.html')

@app.route('/map')
@require_auth
def satellite_map():
    """Satellite map page."""
    return render_template('map.html')

@app.route('/api/weather-correlations')
@require_auth
def api_weather_correlations():
    """API endpoint for weather correlation data."""
    try:
        from src.monitor.weather_integration import WeatherPerformanceAnalyzer
        analyzer = WeatherPerformanceAnalyzer()
        correlations = analyzer.generate_correlation_report(7)  # Last 7 days
        return jsonify(correlations)
    except Exception as e:
        logger.error(f"Error fetching weather correlations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-analysis')
@require_auth
def api_ml_analysis():
    """API endpoint for ML analysis data."""
    try:
        from src.ml.ml_analyzer import MLAnalyzer
        analyzer = MLAnalyzer()
        analysis = analyzer.generate_report(30, 90, 7)  # Anomaly days, forecast days, prediction days
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error fetching ML analysis: {e}")
        return jsonify({'error': str(e)}), 500

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
    
    # Run the application with Flask
    app.run(host=args.host, port=args.port, debug=args.debug)

# Global variable to track if realtime updates have been started
_realtime_updates_started = False

@app.before_request
def start_realtime_updates():
    """Start real-time updates when the first request is made."""
    global _realtime_updates_started
    if not _realtime_updates_started:
        try:
            config_path = app.config.get('CONFIG_PATH', 'config.json')
            start_realtime_updater(config_path)
            logger.info("Real-time updates started")
            _realtime_updates_started = True
        except Exception as e:
            logger.error(f"Failed to start real-time updates: {e}")

if __name__ == "__main__":
    main()