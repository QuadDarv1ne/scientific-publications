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
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Database and logging utilities
from src.database.db_manager import get_database_manager, get_db_session
from src.utils.logging_config import setup_logging, get_logger

# Models and realtime updater
from src.monitor.monitor import PerformanceMetric, Base
from src.database.models import User
from src.web.realtime_manager import start_realtime_updater, stop_realtime_updater

# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

# Language translations dictionary
LANGUAGES = {
    'en': {
        'dashboard': 'Dashboard',
        'enhanced_dashboard': 'Enhanced Dashboard',
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
    'download_mbps': 'Download (Mbps)',
    'upload_mbps': 'Upload (Mbps)',
    'ping_ms': 'Ping (ms)',
    'packet_loss_percent_label': 'Packet Loss (%)',
    'speed_mbps': 'Speed (Mbps)',
        'performance_history_chart': 'Performance History Chart',
        'site_name': 'Starlink Performance Monitor',
        'login_prompt': 'Please sign in',
        'remember_me': 'Remember me',
        'sign_in': 'Sign in',
        'refresh': 'Refresh',
        'auto_refresh': 'Auto Refresh',
        'time_range': 'Time Range',
        'no_alerts': 'No alerts at this time',
        'save_settings': 'Save Settings',
        'reset_defaults': 'Reset to Defaults',
        'general_settings': 'General Settings',
        'notification_settings': 'Notification Settings',
        'performance_thresholds': 'Performance Thresholds',
        'alert_recipients': 'Alert Recipients',
        'email_notifications': 'Email Notifications',
        'telegram_notifications': 'Telegram Notifications',
        'notification_email': 'Notification Email',
        'telegram_chat_id': 'Telegram Chat ID',
        'download_threshold': 'Download Threshold (Mbps)',
        'upload_threshold': 'Upload Threshold (Mbps)',
        'ping_threshold': 'Ping Threshold (ms)',
        'packet_loss_threshold': 'Packet Loss Threshold (%)',
        'apply_settings': 'Apply Settings',
        'cancel': 'Cancel',
        'confirm_reset': 'Are you sure you want to reset all settings to defaults?',
        'yes': 'Yes',
        'no': 'No',
        'ml_predictions': 'ML Predictions',
        'anomaly_detection': 'Anomaly Detection',
        'forecasting': 'Forecasting',
        'model_accuracy': 'Model Accuracy',
        'detected_anomalies': 'Detected Anomalies',
        'prediction_accuracy': 'Prediction Accuracy',
        'next_24_hours': 'Next 24 Hours Prediction',
        'next_7_days': 'Next 7 Days Prediction',
        'performance_trends': 'Performance Trends',
        'export_data': 'Export Data',
        'generate_report': 'Generate Report',
        'report_type': 'Report Type',
        'date_range': 'Date Range',
        'daily_report': 'Daily Report',
        'weekly_report': 'Weekly Report',
        'monthly_report': 'Monthly Report',
        'custom_report': 'Custom Report',
        'generate': 'Generate',
        'download_report': 'Download Report',
        'satellite_map': 'Satellite Map',
        'satellite_details': 'Satellite Details',
        'network_statistics': 'Network Statistics',
        'map_layers': 'Map Layers',
        'street_view': 'Street View',
        'satellite_view': 'Satellite View',
        'terrain_view': 'Terrain View',
        'view_2d': '2D View',
        'view_3d': '3D View',
        'constellation_health': 'Constellation Health',
        'active_satellites': 'Active Satellites',
        'total_satellites': 'Total Satellites',
        'satellite_positions': 'Satellite Positions',
        'export_options': 'Export Options',
        'export_to_csv': 'Export to CSV',
        'export_to_excel': 'Export to Excel',
        'export_to_pdf': 'Export to PDF',
        'compare_periods': 'Compare Periods',
        'advanced_filtering': 'Advanced Filtering',
        'statistical_summary': 'Statistical Summary',
        'percentile_95': '95th Percentile',
        'average': 'Average',
        'minimum': 'Minimum',
        'maximum': 'Maximum',
        'standard_deviation': 'Standard Deviation',
        'connecting_data_stream': 'Connecting to data stream...',
        'line': 'Line',
        'bar': 'Bar',
        'area': 'Area',
        'download_distribution': 'Download Speed Distribution',
        'last_updated': 'Last updated',
        'frequency': 'Frequency',
        'ping_performance': 'Ping Performance',
        'packet_loss_over_time': 'Packet Loss Over Time',
        'performance_summary': 'Performance Summary',
        'export_format': 'Export Format',
        'generate_new_report': 'Generate New Report',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'metrics_to_include': 'Metrics to Include',
        'speed_test_results': 'Speed Test Results',
        'ping_statistics': 'Ping Statistics',
        'weather_correlation': 'Weather Correlation',
        'alert_history': 'Alert History',
        'output_format': 'Output Format',
        'recent_reports': 'Recent Reports',
        'report_name': 'Report Name',
        'type': 'Type',
        'generated': 'Generated',
        'size': 'Size',
        'actions': 'Actions',
        'view': 'View',
        'download': 'Download',
        'report_preview': 'Report Preview',
        'select_report_to_preview': 'Select a report to preview or generate a new report.',
        'view_sample_report': 'View Sample Report',

        'new_alert': 'New Alert',
        'critical': 'Critical',
        'requires_immediate_attention': 'Requires immediate attention',
        'warning': 'Warning',
        'performance_degradation': 'Performance degradation',
        'info': 'Info',
        'informational_alerts': 'Informational alerts',
        'resolved': 'Resolved',
        'recently_resolved': 'Recently resolved',
        'active_alerts': 'Active Alerts',
        'severity': 'Severity',
        'alert': 'Alert',
        'description': 'Description',
        'triggered': 'Triggered',
        'duration': 'Duration',
        'create_new_alert': 'Create New Alert',
        'alert_name': 'Alert Name',
        'metric': 'Metric',
        'condition': 'Condition',
        'threshold_value': 'Threshold Value',
        'notification_method': 'Notification Method',
        'condition_above': 'Above',
        'condition_below': 'Below',
        'condition_equals': 'Equals',
        'both': 'Both',
        'save_alert': 'Save Alert',

        'loading_ml_data': 'Loading ML analysis data...',
        'method': 'Method',
        'total_anomalies': 'Total Anomalies',
        'anomaly_percentage': 'Anomaly Percentage',
        'detailed_anomaly_results': 'Detailed Anomaly Results',
        'isolation_forest': 'Isolation Forest',
        'dbscan': 'DBSCAN',
        'elliptic_envelope': 'Elliptic Envelope',
        'timestamp': 'Timestamp',
        'no_anomaly_data_available': 'No anomaly data available',
        'no_anomalies_detected': 'No anomalies detected',
        'lower_confidence': 'Lower Confidence',
        'upper_confidence': 'Upper Confidence',
        'ml_loaded_success': 'ML analysis data loaded successfully',
        'ml_no_data': 'No ML analysis data available',
        'ml_error': 'Error loading ML analysis data',
        'performance_forecasting': 'Performance Forecasting',

        'snr': 'SNR',
        'obstruction': 'Obstruction',
        'dish_downlink': 'Dish Downlink',
        'dish_uplink': 'Dish Uplink',
        'starlink_dish_metrics': 'Starlink Dish Metrics',
        'low_download_speed_detected': 'Low download speed detected',
        'high_latency_detected': 'High latency detected',
        'high_packet_loss_detected': 'High packet loss detected',
        'high_obstruction_detected': 'High obstruction detected',

        'register': 'Register',
        'create_account': 'Create account',
        'email': 'Email',
        'confirm_password': 'Confirm password',
        'no_account': "Don't have an account?",
        'have_account': 'Already have an account?',
        'forgot_password': 'Forgot password?',
        'password_reset': 'Password reset',
        'send_reset_link': 'Send reset link',
        'back_to_login': 'Back to login',
        'reset_link': 'Reset link',
        'invalid_or_expired_link': 'The reset link is invalid or expired',
        'set_new_password': 'Set new password',
        'password_updated_message': 'Password updated. You can sign in now.',
        'fields_required': 'Please fill in all fields',
        'passwords_mismatch': 'Passwords do not match',
        'password_min_length': 'Password must be at least 6 characters long',
        'user_exists': 'A user with this name or email already exists',
        'registration_success': 'Account created. You can sign in now.',
        'registration_error': 'Registration error',
        'reset_request_error': 'Error requesting password reset',
        'reset_error': 'Password reset error',

        # UI controls and accessibility
        'toggle_menu': 'Toggle menu',

        # Settings navigation and labels
        'navigation': 'Navigation',
        'general': 'General',
        'monitoring': 'Monitoring',
        'notifications': 'Notifications',
        'database': 'Database',
        'web_interface': 'Web Interface',
        'weather_integration': 'Weather Integration',
        'user_management': 'User Management',
        'timezone': 'Time zone',
        'language': 'Language',
        'auto_update': 'Auto update',
        'monitoring_settings': 'Monitoring Settings',
        'monitoring_interval': 'Monitoring Interval',
        'minutes': 'minutes',
        'speed_test_config': 'Speed Test Configuration',
        'enable_speed_tests': 'Enable speed tests',
        'use_specific_servers': 'Use specific servers',
        'server_ids': 'Server IDs (comma-separated)',
        'ping_test_config': 'Ping Test Configuration',
        'enable_ping_tests': 'Enable ping tests',
        'server_name': 'Server name',
        'ip_address': 'IP address',
        'add_server': 'Add server',
        'enable_telegram': 'Enable Telegram notifications',
        'bot_token': 'Bot token',
        'chat_id': 'Chat ID',
        'enable_email': 'Enable email notifications',
        'smtp_server': 'SMTP server',
        'port': 'Port',
        'role': 'Role',
        'last_login': 'Last login',
        'administrator': 'Administrator',
        'edit': 'Edit',
        'delete': 'Delete',
        'add_user': 'Add user',
        'add_new_user': 'Add new user',
        'enter_username': 'Enter username',
        'enter_password': 'Enter password',
        'web_interface_settings': 'Web Interface Settings',
        'enable_debug_mode': 'Enable debug mode',
        'authentication': 'Authentication',
        'enable_authentication': 'Enable authentication',
        'manage_users': 'Manage users',
        'database_settings': 'Database Settings',
        'database_type': 'Database type',
        'host': 'Host',
        'database_name': 'Database name',
        'enable_weather_integration': 'Enable weather integration',
        'api_key': 'API key',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'weather_parameters': 'Weather parameters',
        'temperature': 'Temperature',
        'precipitation': 'Precipitation',
        'wind_speed': 'Wind speed',
        'cloud_cover': 'Cloud cover',
        'reset_confirmation': 'This will reset all settings to defaults. Proceed?',
        'settings_saved': 'Settings saved',
        'settings_reset': 'Settings reset to defaults',
        'user': 'User',

        # Performance page
        'last_30_days': 'Last 30 Days',
        'export': 'Export',
        'csv': 'CSV',
        'json': 'JSON',
        'pdf': 'PDF',
        'excel': 'Excel',
        'compare': 'Compare',
        'advanced_filters': 'Advanced Filters',
        'metric_type': 'Metric Type',
        'all_metrics': 'All Metrics',
        'server': 'Server',
        'all_servers': 'All Servers',
        'select_date_range': 'Select date range',
        'performance_threshold': 'Performance Threshold',
        'all_data': 'All Data',
        'poor_performance': 'Poor Performance (< 25th percentile)',
        'good_performance': 'Good Performance (> 75th percentile)',
        'outliers': 'Outliers (> 95th percentile)',
        'min_download': 'Min Download (Mbps)',
        'max_ping': 'Max Ping (ms)',
        'max_packet_loss': 'Max Packet Loss (%)',
        'apply_filters': 'Apply Filters',
        'performance_distribution': 'Performance Distribution',
        'raw_data': 'Raw Data',
        'metric': 'Metric',
        'min': 'Min',
        'avg': 'Avg',
        'std_dev': 'Std Dev',
        'performance_index': 'Performance Index',
        'showing': 'Showing',
        'to': 'to',
        'of': 'of',
        'entries': 'entries',
        'rows': 'rows',
        'performance_comparison': 'Performance Comparison',
        'period_1': 'Period 1',
        'period_2': 'Period 2',
        'close': 'Close',
        'exporting_data': 'Exporting data as',
        'comparing_periods': 'Comparing periods',
        # Map / Satellite UI
        'satellite_map': 'Satellite Map',
        'map_layers': 'Map Layers',
        'street_view': 'Street Map',
        'satellite_view': 'Satellite View',
        'terrain_view': 'Terrain View',
        'satellite_positions': 'Satellite Positions',
        'satellite_details': 'Satellite Details',
        'loading_satellite_data': 'Loading satellite data...',
        'no_satellite_data': 'No satellite data available',
        'satellite_id': 'Satellite ID',
        'altitude_km': 'Altitude (km)',
        'speed_kms': 'Speed (km/s)',
        'status_label': 'Status',
        'moving_satellites': 'Moving',
        'in_coverage': 'In Coverage',
        'switched_to_2d': 'Switched to 2D map view',
        'switched_to_3d': 'Switched to 3D globe view',
        'initialized_success': 'initialized successfully',
        'data_loaded_success': 'data loaded successfully',
        'error_loading_satellite_data': 'Error loading satellite data',
        'active_satellite': 'Active Satellite',
        'inactive_satellite': 'Inactive Satellite',
        'moving_satellite': 'Moving Satellite',
    'legend': 'Legend',
    'close': 'Close',

        # Settings extras
        'timezone_utc': 'UTC',
        'timezone_eastern': 'Eastern Time (US & Canada)',
        'timezone_london': 'London',
        'timezone_tokyo': 'Tokyo',
        'timezone_moscow': 'Moscow',
        'sqlite_embedded': 'SQLite (Embedded)',
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'placeholder_bot_token': 'YOUR_BOT_TOKEN_HERE',
        'placeholder_chat_id': 'YOUR_CHAT_ID_HERE',
        'smtp_placeholder': 'smtp.gmail.com',
        'email_placeholder': 'your.email@gmail.com'
    },
    'ru': {
        'dashboard': 'Панель управления',
        'enhanced_dashboard': 'Расширенная панель',
        'performance': 'Производительность',
        'alerts': 'Оповещения',
        'reports': 'Отчеты',
        'settings': 'Настройки',
        'ml_analysis': 'ML анализ',
        'logout': 'Выйти',
        'login': 'Вход',
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
    'download_mbps': 'Загрузка (Мбит/с)',
    'upload_mbps': 'Отдача (Мбит/с)',
    'ping_ms': 'Пинг (мс)',
    'packet_loss_percent_label': 'Потери пакетов (%)',
    'speed_mbps': 'Скорость (Мбит/с)',
        'performance_history_chart': 'График истории производительности',
        'site_name': 'Монитор производительности Starlink',
        'login_prompt': 'Пожалуйста, войдите',
        'remember_me': 'Запомнить меня',
        'sign_in': 'Войти',
        'refresh': 'Обновить',
        'auto_refresh': 'Автообновление',
        'time_range': 'Временной диапазон',
        'no_alerts': 'На данный момент нет оповещений',
        'save_settings': 'Сохранить настройки',
        'reset_defaults': 'Сбросить к значениям по умолчанию',
        'general_settings': 'Общие настройки',
        'notification_settings': 'Настройки уведомлений',
        'performance_thresholds': 'Пороги производительности',
        'alert_recipients': 'Получатели оповещений',
        'email_notifications': 'Уведомления по электронной почте',
        'telegram_notifications': 'Уведомления Telegram',
        'notification_email': 'Email для уведомлений',
        'telegram_chat_id': 'ID чата Telegram',
        'download_threshold': 'Порог загрузки (Мбит/с)',
        'upload_threshold': 'Порог отдачи (Мбит/с)',
        'ping_threshold': 'Порог пинга (мс)',
        'packet_loss_threshold': 'Порог потерь пакетов (%)',
        'apply_settings': 'Применить настройки',
        'cancel': 'Отмена',
        'confirm_reset': 'Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?',
        'yes': 'Да',
        'no': 'Нет',
        'ml_predictions': 'ML прогнозы',
        'anomaly_detection': 'Обнаружение аномалий',
        'forecasting': 'Прогнозирование',
        'model_accuracy': 'Точность модели',
        'detected_anomalies': 'Обнаруженные аномалии',
        'prediction_accuracy': 'Точность прогноза',
        'next_24_hours': 'Прогноз на 24 часа',
        'next_7_days': 'Прогноз на 7 дней',
        'performance_trends': 'Тренды производительности',
        'export_data': 'Экспорт данных',
        'generate_report': 'Сгенерировать отчет',
        'report_type': 'Тип отчета',
        'date_range': 'Диапазон дат',
        'daily_report': 'Ежедневный отчет',
        'weekly_report': 'Еженедельный отчет',
        'monthly_report': 'Ежемесячный отчет',
        'custom_report': 'Пользовательский отчет',
        'generate': 'Сгенерировать',
        'download_report': 'Скачать отчет',
        'satellite_map': 'Карта спутников',
        'satellite_details': 'Детали спутника',
        'network_statistics': 'Статистика сети',
        'map_layers': 'Слои карты',
        'street_view': 'Уличный вид',
        'satellite_view': 'Вид со спутника',
        'terrain_view': 'Рельеф',
        'view_2d': '2D вид',
        'view_3d': '3D вид',
        'constellation_health': 'Состояние созвездия',
        'active_satellites': 'Активные спутники',
        'total_satellites': 'Всего спутников',
        'satellite_positions': 'Позиции спутников',
        'export_options': 'Опции экспорта',
        'export_to_csv': 'Экспорт в CSV',
        'export_to_excel': 'Экспорт в Excel',
        'export_to_pdf': 'Экспорт в PDF',
        'compare_periods': 'Сравнить периоды',
        'advanced_filtering': 'Расширенная фильтрация',
        'statistical_summary': 'Статистическая сводка',
        'percentile_95': '95-й процентиль',
        'average': 'Среднее',
        'minimum': 'Минимум',
        'maximum': 'Максимум',
        'standard_deviation': 'Стандартное отклонение',
        'connecting_data_stream': 'Подключение к потоку данных...',
        'line': 'Линия',
        'bar': 'Столбец',
        'area': 'Область',
        'download_distribution': 'Распределение скорости загрузки',
        'last_updated': 'Последнее обновление',
        'frequency': 'Частота',
        'ping_performance': 'Производительность пинга',
        'packet_loss_over_time': 'Потери пакетов во времени',
        'performance_summary': 'Сводка производительности',
        'export_format': 'Формат экспорта',
        'generate_new_report': 'Создать новый отчет',
        'start_date': 'Дата начала',
        'end_date': 'Дата окончания',
        'metrics_to_include': 'Включаемые метрики',
        'speed_test_results': 'Результаты спид-теста',
        'ping_statistics': 'Статистика пинга',
        'weather_correlation': 'Корреляция с погодой',
        'alert_history': 'История оповещений',
        'output_format': 'Формат вывода',
        'recent_reports': 'Недавние отчеты',
        'report_name': 'Название отчета',
        'type': 'Тип',
        'generated': 'Сгенерирован',
        'size': 'Размер',
        'actions': 'Действия',
        'view': 'Просмотр',
        'download': 'Скачать',
        'report_preview': 'Предпросмотр отчета',
        'select_report_to_preview': 'Выберите отчет для просмотра или создайте новый.',
        'view_sample_report': 'Посмотреть пример отчета',

        'new_alert': 'Новое оповещение',
        'critical': 'Критично',
        'requires_immediate_attention': 'Требует немедленного внимания',
        'warning': 'Предупреждение',
        'performance_degradation': 'Ухудшение производительности',
        'info': 'Инфо',
        'informational_alerts': 'Информационные оповещения',
        'resolved': 'Решено',
        'recently_resolved': 'Недавно устранено',
        'active_alerts': 'Активные оповещения',
        'severity': 'Важность',
        'alert': 'Событие',
        'description': 'Описание',
        'triggered': 'Сработало',
        'duration': 'Длительность',
        'create_new_alert': 'Создать оповещение',
        'alert_name': 'Название оповещения',
        'metric': 'Метрика',
        'condition': 'Условие',
        'threshold_value': 'Пороговое значение',
        'notification_method': 'Способ уведомления',
        'condition_above': 'Больше',
        'condition_below': 'Меньше',
        'condition_equals': 'Равно',
        'both': 'Оба',
        'save_alert': 'Сохранить оповещение',

        'loading_ml_data': 'Загрузка данных ML-анализа...',
        'method': 'Метод',
        'total_anomalies': 'Всего аномалий',
        'anomaly_percentage': 'Доля аномалий',
        'detailed_anomaly_results': 'Детальные результаты аномалий',
        'isolation_forest': 'Isolation Forest',
        'dbscan': 'DBSCAN',
        'elliptic_envelope': 'Elliptic Envelope',
        'timestamp': 'Метка времени',
        'no_anomaly_data_available': 'Нет данных об аномалиях',
        'no_anomalies_detected': 'Аномалии не обнаружены',
        'lower_confidence': 'Нижняя граница доверия',
        'upper_confidence': 'Верхняя граница доверия',
        'ml_loaded_success': 'Данные ML-анализа успешно загружены',
        'ml_no_data': 'Нет данных ML-анализа',
        'ml_error': 'Ошибка загрузки данных ML-анализа',
        'performance_forecasting': 'Прогнозирование производительности',

        'snr': 'SNR',
        'obstruction': 'Заслонение',
        'dish_downlink': 'Спутниковый даунлинк',
        'dish_uplink': 'Спутниковый аплинк',
        'starlink_dish_metrics': 'Метрики тарелки Starlink',
        'low_download_speed_detected': 'Обнаружена низкая скорость загрузки',
        'high_latency_detected': 'Обнаружена высокая задержка',
        'high_packet_loss_detected': 'Обнаружены высокие потери пакетов',
        'high_obstruction_detected': 'Обнаружено высокое заслонение',

        'register': 'Регистрация',
        'create_account': 'Создать аккаунт',
        'email': 'Email',
        'confirm_password': 'Повторите пароль',
        'no_account': 'Нет аккаунта?',
        'have_account': 'У меня уже есть аккаунт',
        'forgot_password': 'Забыли пароль?',
        'password_reset': 'Восстановление пароля',
        'send_reset_link': 'Отправить ссылку для сброса',
        'back_to_login': 'Назад к входу',
        'reset_link': 'Ссылка на сброс',
        'invalid_or_expired_link': 'Ссылка сброса недействительна или истекла',
        'set_new_password': 'Установить новый пароль',
        'password_updated_message': 'Пароль обновлён. Теперь вы можете войти.',
        'fields_required': 'Заполните все поля',
        'passwords_mismatch': 'Пароли не совпадают',
        'password_min_length': 'Пароль должен быть не короче 6 символов',
        'user_exists': 'Пользователь с таким именем или email уже существует',
        'registration_success': 'Аккаунт создан. Теперь вы можете войти.',
        'registration_error': 'Ошибка регистрации',
        'reset_request_error': 'Ошибка запроса сброса пароля',
        'reset_error': 'Ошибка сброса пароля',

        # UI controls and accessibility
        'toggle_menu': 'Переключить меню',

        # Settings navigation and labels
        'navigation': 'Навигация',
        'general': 'Общее',
        'monitoring': 'Мониторинг',
        'notifications': 'Уведомления',
        'database': 'База данных',
        'web_interface': 'Веб-интерфейс',
        'weather_integration': 'Интеграция с погодой',
        'user_management': 'Управление пользователями',
        'timezone': 'Часовой пояс',
        'language': 'Язык',
        'auto_update': 'Автообновление',
        'monitoring_settings': 'Настройки мониторинга',
        'monitoring_interval': 'Интервал мониторинга',
        'minutes': 'минут',
        'speed_test_config': 'Настройки спид-теста',
        'enable_speed_tests': 'Включить спид-тесты',
        'use_specific_servers': 'Использовать конкретные серверы',
        'server_ids': 'ID серверов (через запятую)',
        'ping_test_config': 'Настройки пинг-теста',
        'enable_ping_tests': 'Включить пинг-тесты',
        'server_name': 'Имя сервера',
        'ip_address': 'IP-адрес',
        'add_server': 'Добавить сервер',
        'enable_telegram': 'Включить уведомления Telegram',
        'bot_token': 'Токен бота',
        'chat_id': 'ID чата',
        'enable_email': 'Включить email-уведомления',
        'smtp_server': 'SMTP сервер',
        'port': 'Порт',
        'role': 'Роль',
        'last_login': 'Последний вход',
        'administrator': 'Администратор',
        'edit': 'Редактировать',
        'delete': 'Удалить',
        'add_user': 'Добавить пользователя',
        'add_new_user': 'Добавить нового пользователя',
        'enter_username': 'Введите имя пользователя',
        'enter_password': 'Введите пароль',
        'web_interface_settings': 'Настройки веб-интерфейса',
        'enable_debug_mode': 'Включить режим отладки',
        'authentication': 'Аутентификация',
        'enable_authentication': 'Включить аутентификацию',
        'manage_users': 'Управление пользователями',
        'database_settings': 'Настройки базы данных',
        'database_type': 'Тип базы данных',
        'host': 'Хост',
        'database_name': 'Имя базы данных',
        'enable_weather_integration': 'Включить интеграцию с погодой',
        'api_key': 'API ключ',
        'latitude': 'Широта',
        'longitude': 'Долгота',
        'weather_parameters': 'Параметры погоды',
        'temperature': 'Температура',
        'precipitation': 'Осадки',
        'wind_speed': 'Скорость ветра',
        'cloud_cover': 'Облачность',
        'reset_confirmation': 'Это действие сбросит все настройки по умолчанию. Продолжить?',
        'settings_saved': 'Настройки сохранены',
        'settings_reset': 'Настройки сброшены к значениям по умолчанию',
        'user': 'Пользователь',

        # Performance page
        'last_30_days': 'Последние 30 дней',
        'export': 'Экспорт',
        'csv': 'CSV',
        'json': 'JSON',
        'pdf': 'PDF',
        'excel': 'Excel',
        'compare': 'Сравнить',
        'advanced_filters': 'Расширенные фильтры',
        'metric_type': 'Тип метрики',
        'all_metrics': 'Все метрики',
        'server': 'Сервер',
        'all_servers': 'Все серверы',
        'select_date_range': 'Выберите диапазон дат',
        'performance_threshold': 'Порог производительности',
        'all_data': 'Все данные',
        'poor_performance': 'Плохая производительность (< 25-й процентиль)',
        'good_performance': 'Хорошая производительность (> 75-й процентиль)',
        'outliers': 'Выбросы (> 95-й процентиль)',
        'min_download': 'Мин. загрузка (Мбит/с)',
        'max_ping': 'Макс. пинг (мс)',
        'max_packet_loss': 'Макс. потери пакетов (%)',
        'apply_filters': 'Применить фильтры',
        'performance_distribution': 'Распределение производительности',
        'raw_data': 'Исходные данные',
        'metric': 'Метрика',
        'min': 'Мин',
        'avg': 'Средн',
        'std_dev': 'СКО',
        'performance_index': 'Индекс производительности',
        'showing': 'Показаны',
        'to': 'по',
        'of': 'из',
        'entries': 'записей',
        'rows': 'строк',
        'performance_comparison': 'Сравнение производительности',
        'period_1': 'Период 1',
        'period_2': 'Период 2',
        'close': 'Закрыть',
    'exporting_data': 'Экспорт данных как',
    'comparing_periods': 'Сравнение периодов',
    # Карта / Спутники
    'satellite_map': 'Карта спутников',
    'map_layers': 'Слои карты',
    'street_view': 'Уличный вид',
    'satellite_view': 'Вид со спутника',
    'terrain_view': 'Рельеф',
    'satellite_positions': 'Позиции спутников',
    'satellite_details': 'Детали спутника',
    'loading_satellite_data': 'Загрузка данных спутников...',
    'no_satellite_data': 'Нет данных по спутникам',
    'satellite_id': 'ID спутника',
    'altitude_km': 'Высота (км)',
    'speed_kms': 'Скорость (км/с)',
    'status_label': 'Статус',
    'moving_satellites': 'Движение',
    'in_coverage': 'В зоне покрытия',
    'switched_to_2d': 'Переключено на 2D карту',
    'switched_to_3d': 'Переключено на 3D глобус',
    'initialized_success': 'успешно инициализирована',
    'data_loaded_success': 'данные успешно загружены',
    'error_loading_satellite_data': 'Ошибка загрузки данных спутников',
    'active_satellite': 'Активный спутник',
    'inactive_satellite': 'Неактивный спутник',
    'moving_satellite': 'Движущийся спутник',
    'legend': 'Легенда',
    'close': 'Закрыть',

    # Settings extras
    'timezone_utc': 'UTC',
    'timezone_eastern': 'Североамериканское восточное время',
    'timezone_london': 'Лондон',
    'timezone_tokyo': 'Токио',
    'timezone_moscow': 'Москва',
    'sqlite_embedded': 'SQLite (встроенная)',
    'postgresql': 'PostgreSQL',
    'mysql': 'MySQL',
    'placeholder_bot_token': 'ВАШ_ТОКЕН_БОТА_ЗДЕСЬ',
    'placeholder_chat_id': 'ВАШ_CHAT_ID_ЗДЕСЬ',
    'smtp_placeholder': 'smtp.gmail.com',
    'email_placeholder': 'your.email@gmail.com'
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
    return render_template('dashboard.html')

@app.route('/enhanced')
@require_auth
def enhanced_dashboard():
    """Enhanced dashboard with Starlink-specific metrics."""
    return render_template('enhanced_starlink_dashboard.html')

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

@app.route('/api/metrics/latest')
@require_auth
def get_latest_metrics():
    """API endpoint to get the latest metrics including Starlink dish data."""
    try:
        session = get_db_session()
        latest_metric = session.query(PerformanceMetric).order_by(PerformanceMetric.timestamp.desc()).first()
        session.close()
        
        if latest_metric:
            return jsonify({
                'download_mbps': latest_metric.download_mbps,
                'upload_mbps': latest_metric.upload_mbps,
                'ping_ms': latest_metric.ping_ms,
                'packet_loss_percent': latest_metric.packet_loss_percent,
                'server_name': latest_metric.server_name,
                'timestamp': latest_metric.timestamp.isoformat(),
                'snr': latest_metric.snr,
                'obstruction_fraction': latest_metric.obstruction_fraction,
                'downlink_throughput_mbps': latest_metric.downlink_throughput_mbps,
                'uplink_throughput_mbps': latest_metric.uplink_throughput_mbps
            })
        else:
            # Return mock data if no metrics available
            return jsonify({
                'download_mbps': 85.2,
                'upload_mbps': 15.7,
                'ping_ms': 25.3,
                'packet_loss_percent': 0.5,
                'server_name': 'Mock Data',
                'timestamp': datetime.utcnow().isoformat(),
                'snr': 15.8,
                'obstruction_fraction': 0.02,
                'downlink_throughput_mbps': 85.2,
                'uplink_throughput_mbps': 15.7
            })
    except Exception as e:
        logger.error(f"Error fetching latest metrics: {e}")
        return jsonify({
            'download_mbps': 0,
            'upload_mbps': 0,
            'ping_ms': 0,
            'packet_loss_percent': 0,
            'server_name': 'Error',
            'timestamp': datetime.utcnow().isoformat(),
            'snr': 0,
            'obstruction_fraction': 0,
            'downlink_throughput_mbps': 0,
            'uplink_throughput_mbps': 0
        })

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    # If auth disabled, redirect to dashboard
    web_app = WebApp(app.config.get('CONFIG_PATH', 'config.json'))
    if not web_app.is_auth_enabled():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not email or not password:
            return render_template('register.html', error='Заполните все поля')
        if password != confirm:
            return render_template('register.html', error='Пароли не совпадают')
        if len(password) < 6:
            return render_template('register.html', error='Пароль должен быть не короче 6 символов')

        db = get_db_session()
        try:
            # Check duplicates
            if db.query(User).filter((User.username == username) | (User.email == email)).first():
                return render_template('register.html', error='Пользователь с таким именем или email уже существует')
            # Create user
            pwd_hash = generate_password_hash(password)
            user = User(username=username, email=email, password_hash=pwd_hash, role='user')
            db.add(user)
            db.commit()
            return render_template('register.html', message='Аккаунт создан. Теперь вы можете войти.')
        except Exception as e:
            logger.error(f"Registration error: {e}")
            db.rollback()
            return render_template('register.html', error='Ошибка регистрации')
        finally:
            db.close()

    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request page."""
    web_app = WebApp(app.config.get('CONFIG_PATH', 'config.json'))
    if not web_app.is_auth_enabled():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            return render_template('forgot_password.html', error='Укажите email')
        db = get_db_session()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # Do not reveal that user does not exist
                return render_template('forgot_password.html', message='Если такой email существует, ссылка отправлена')
            # Generate token
            token = secrets.token_urlsafe(32)
            user.set_reset_token(token, validity_minutes=30)
            db.commit()

            reset_link = url_for('reset_password', token=token, _external=True)
            logger.info(f"Password reset link for {email}: {reset_link}")
            # If email notifications configured, here we could send the email
            return render_template('forgot_password.html', message='Ссылка для сброса отправлена', reset_link=reset_link)
        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            db.rollback()
            return render_template('forgot_password.html', error='Ошибка запроса сброса пароля')
        finally:
            db.close()

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token: str):
    """Password reset page."""
    web_app = WebApp(app.config.get('CONFIG_PATH', 'config.json'))
    if not web_app.is_auth_enabled():
        return redirect(url_for('dashboard'))

    db = get_db_session()
    try:
        user = db.query(User).filter(User.reset_token == token).first()
        valid = bool(user and user.reset_token_valid())
        if request.method == 'POST':
            if not valid:
                return render_template('reset_password.html', valid=False)
            password = request.form.get('password', '')
            confirm = request.form.get('confirm', '')
            if password != confirm:
                return render_template('reset_password.html', valid=True, error='Пароли не совпадают')
            if len(password) < 6:
                return render_template('reset_password.html', valid=True, error='Пароль должен быть не короче 6 символов')
            user.password_hash = generate_password_hash(password)
            user.clear_reset_token()
            db.commit()
            return render_template('reset_password.html', valid=False, message='Пароль обновлён. Теперь вы можете войти.')
        return render_template('reset_password.html', valid=valid)
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        db.rollback()
        return render_template('reset_password.html', valid=False, error='Ошибка сброса пароля')
    finally:
        db.close()

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

        # First try DB users
        try:
            db = get_db_session()
            user = db.query(User).filter(User.username == username, User.is_active == True).first()
            if user:
                # Support both werkzeug hash and legacy sha256 saved in password_hash
                if (user.password_hash and user.password_hash.startswith('pbkdf2:')):
                    if check_password_hash(user.password_hash, password):
                        return True
                else:
                    legacy_hash = hashlib.sha256(password.encode()).hexdigest()
                    if user.password_hash == legacy_hash:
                        return True
        except Exception as e:
            logger.error(f"DB auth error: {e}")
        finally:
            try:
                db.close()
            except Exception:
                pass

        # Fallback to users in config.json
        users = auth_config.get('users', [])
        for user in users:
            if user.get('username') == username:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if user.get('password_hash') == hashed_password:
                    return True
        return False

    def is_auth_enabled(self) -> bool:
        web_config = self.config.get('web', {})
        auth_config = web_config.get('auth', {})
        return auth_config.get('enabled', False)
        
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