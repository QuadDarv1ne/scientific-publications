#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web interface for ISS Telemetry Analyzer
Веб-интерфейс для анализатора телеметрии МКС
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent))

from src.iss_orbital_analysis import ISSTracker, analyze_pass_frequency
from src.iss_environment_analysis import ISSEnvironmentAnalyzer
from src.utils import FileManager

app = Flask(__name__, template_folder='templates', static_folder='static')

# Глобальные переменные для хранения данных
tracker = ISSTracker()
analyzer = ISSEnvironmentAnalyzer()

# Разрешить обслуживание статических файлов
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

def fig_to_base64(fig):
    """Конвертация matplotlib figure в base64 строку"""
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/current_position')
def current_position():
    """API для получения текущего положения МКС"""
    try:
        position = tracker.get_current_position()
        if position:
            return jsonify({
                'success': True,
                'data': {
                    'latitude': position['latitude'],
                    'longitude': position['longitude'],
                    'timestamp': position['timestamp'].isoformat() if hasattr(position['timestamp'], 'isoformat') else str(position['timestamp'])
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Не удалось получить текущее положение'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/orbital_parameters')
def orbital_parameters():
    """API для получения орбитальных параметров"""
    try:
        # Сбор данных (симуляция)
        tracker.collect_positions(duration_minutes=1, interval_seconds=10)
        
        # Расчет параметров
        params = tracker.calculate_orbital_parameters()
        if params:
            return jsonify({
                'success': True,
                'data': params
            })
        else:
            # Возвращаем симулированные данные
            simulated_params = {
                'altitude_km': 408.0,
                'avg_speed_kmh': 27600,
                'max_speed_kmh': 27800,
                'min_speed_kmh': 27400,
                'speed_std': 100,
                'orbital_period_min': 92.9,
                'vitkov_per_day': 15.5,
                'data_points': 6
            }
            return jsonify({
                'success': True,
                'data': simulated_params
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ground_track')
def ground_track():
    """API для получения трека МКС"""
    try:
        # Создание графика
        fig = plt.figure(figsize=(10, 6))
        
        # Симулированные данные трека
        time_points = np.linspace(0, 3, 50)
        latitudes = 51.6 * np.sin(2 * np.pi * time_points / 1.5)
        longitudes = (time_points * 15) % 360 - 180
        
        # Мировая карта (упрощенная)
        world_map = np.zeros((180, 360))
        plt.imshow(world_map, cmap='Blues', extent=(-180, 180, -90, 90), alpha=0.3)
        
        # Трек МКС
        plt.plot(longitudes, latitudes, 'r-', linewidth=2, alpha=0.8, label='Трек МКС')
        plt.scatter(longitudes[::5], latitudes[::5], c='red', s=30, alpha=0.7, zorder=5)
        
        # Текущее положение
        plt.scatter(longitudes[-1], latitudes[-1], c='orange', s=100, 
                   marker='*', edgecolors='black', linewidth=1, 
                   label='Текущее положение', zorder=10)
        
        plt.xlabel('Долгота (градусы)')
        plt.ylabel('Широта (градусы)')
        plt.title('Трек Международной космической станции')
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        
        # Конвертация в base64
        img_str = fig_to_base64(fig)
        
        return jsonify({
            'success': True,
            'image': img_str
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/environmental_conditions')
def environmental_conditions():
    """API для получения условий окружающей среды"""
    try:
        # Симуляция данных
        time_t, internal_temp, external_temp = analyzer.simulate_temperature_profile(100, 24)
        time_r, radiation = analyzer.simulate_radiation_levels(100, 24)
        time_a, altitude = analyzer.simulate_altitude_profile(100, 24)
        
        # Создание графиков
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # График 1: Температура
        ax1 = axes[0]
        ax1.plot(time_t, internal_temp, 'b-', linewidth=2, label='Внутри модулей')
        ax1.plot(time_t, external_temp, 'r-', linewidth=2, label='Внешняя оболочка')
        ax1.set_xlabel('Время (часы)')
        ax1.set_ylabel('Температура (°C)')
        ax1.set_title('Температурный профиль МКС')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # График 2: Радиация
        ax2 = axes[1]
        ax2.plot(time_r, radiation, 'purple', linewidth=2)
        ax2.set_xlabel('Время (часы)')
        ax2.set_ylabel('Доза радиации (мкЗв/час)')
        ax2.set_title('Уровень космической радиации на МКС')
        ax2.grid(True, alpha=0.3)
        
        # График 3: Высота орбиты
        ax3 = axes[2]
        ax3.plot(time_a, altitude, 'green', linewidth=2)
        ax3.set_xlabel('Время (часы)')
        ax3.set_ylabel('Высота орбиты (км)')
        ax3.set_title('Высота орбиты МКС')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Конвертация в base64
        img_str = fig_to_base64(fig)
        
        return jsonify({
            'success': True,
            'image': img_str
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/radiation_analysis')
def radiation_analysis():
    """API для анализа радиации"""
    try:
        # Симуляция данных
        hours = 30 * 24  # 30 дней
        time_h, radiation = analyzer.simulate_radiation_levels(hours, hours)
        
        # Накопленная доза
        cumulative_dose = np.cumsum(radiation) * (hours / len(radiation))
        total_dose_mSv = cumulative_dose[-1] / 1000
        
        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 6))
        
        time_days = np.linspace(0, 30, len(cumulative_dose))
        cumulative_dose_mSv = cumulative_dose / 1000
        
        ax.plot(time_days, cumulative_dose_mSv, 'purple', linewidth=2)
        ax.fill_between(time_days, 0, cumulative_dose_mSv, alpha=0.3, color='purple')
        
        ax.set_xlabel('Время (дни)')
        ax.set_ylabel('Накопленная доза (мЗв)')
        ax.set_title(f'Накопленная радиационная доза на МКС ({total_dose_mSv:.2f} мЗв за 30 дней)')
        ax.grid(True, alpha=0.3)
        
        # Конвертация в base64
        img_str = fig_to_base64(fig)
        
        return jsonify({
            'success': True,
            'image': img_str,
            'total_dose_mSv': total_dose_mSv
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/visibility_prediction', methods=['POST'])
def visibility_prediction():
    """API для прогноза видимости"""
    try:
        data = request.get_json()
        latitude = float(data.get('latitude', 55.7558))  # Москва по умолчанию
        longitude = float(data.get('longitude', 37.6173))
        n_passes = int(data.get('n_passes', 5))
        
        # Симуляция прогноза
        passes = []
        for i in range(n_passes):
            hours_ahead = (i + 1) * 1.5
            from datetime import datetime, timedelta
            pass_time = datetime.now() + timedelta(hours=hours_ahead)
            
            duration = np.random.randint(300, 600)
            max_elevation = np.random.randint(10, 80)
            brightness = np.random.uniform(-2, -1)
            
            passes.append({
                'time': pass_time.strftime('%d.%m.%Y %H:%M'),
                'duration': f"{duration//60} мин",
                'elevation': f"{max_elevation}°",
                'brightness': f"{brightness:.1f}m"
            })
        
        return jsonify({
            'success': True,
            'passes': passes,
            'location': {
                'latitude': latitude,
                'longitude': longitude
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/pass_frequency', methods=['POST'])
def pass_frequency():
    """API для анализа частоты пролетов"""
    try:
        data = request.get_json()
        latitude = float(data.get('latitude', 55.7558))  # Москва по умолчанию
        longitude = float(data.get('longitude', 37.6173))
        days = int(data.get('days', 7))
        
        # Анализ частоты пролетов
        passes_per_day = []
        for day in range(days):
            daily_passes = np.random.poisson(4.5)
            passes_per_day.append(daily_passes)
        
        passes_per_day = np.array(passes_per_day)
        total_passes = int(np.sum(passes_per_day))
        avg_passes = float(np.mean(passes_per_day))
        max_passes = int(np.max(passes_per_day))
        min_passes = int(np.min(passes_per_day))
        
        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 6))
        days_range = np.arange(1, days + 1)
        bars = ax.bar(days_range, passes_per_day, color='skyblue', alpha=0.7, edgecolor='navy')
        ax.set_xlabel('Дни')
        ax.set_ylabel('Количество пролетов')
        ax.set_title(f'Частота пролетов МКС над точкой ({latitude}°, {longitude}°)')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=avg_passes, color='red', linestyle='--', linewidth=2, 
                  label=f'Среднее: {avg_passes:.1f}')
        ax.legend()
        
        # Конвертация в base64
        img_str = fig_to_base64(fig)
        
        return jsonify({
            'success': True,
            'image': img_str,
            'statistics': {
                'total_passes': total_passes,
                'avg_passes_per_day': avg_passes,
                'max_passes_per_day': max_passes,
                'min_passes_per_day': min_passes
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)