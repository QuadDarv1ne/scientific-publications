#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web interface for ISS Telemetry Analyzer
Веб-интерфейс для анализатора телеметрии МКС
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, make_response
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
import base64
from io import BytesIO, StringIO
from datetime import datetime, timedelta

app = Flask(__name__)

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
        # Симуляция данных
        position = {
            'latitude': 51.6,
            'longitude': -123.4,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': position
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
        # Симулированные данные
        params = {
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
            'data': params
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
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Симулированные данные трека
        time_points = np.linspace(0, 3, 50)
        latitudes = 51.6 * np.sin(2 * np.pi * time_points / 1.5)
        longitudes = (time_points * 15) % 360 - 180
        
        # Простая визуализация трека
        ax.plot(longitudes, latitudes, 'r-', linewidth=2, alpha=0.8, label='Трек МКС')
        ax.scatter(longitudes[::5], latitudes[::5], c='red', s=30, alpha=0.7, zorder=5)
        
        # Текущее положение
        ax.scatter(longitudes[-1], latitudes[-1], c='orange', s=100, 
                   marker='*', edgecolors='black', linewidth=1, 
                   label='Текущее положение', zorder=10)
        
        ax.set_xlabel('Долгота (градусы)')
        ax.set_ylabel('Широта (градусы)')
        ax.set_title('Трек Международной космической станции')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        
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
        time_t = np.linspace(0, 24, 100)
        internal_temp = 22 + 2 * np.sin(2 * np.pi * time_t / 12)
        external_temp = 40 + (121 - 40) * np.sin(np.pi * (time_t % 1.5) / 1.5)
        
        time_r = np.linspace(0, 24, 100)
        radiation = 30 + 10 * np.sin(2 * np.pi * time_r / 1.5)
        
        time_a = np.linspace(0, 24, 100)
        altitude = 408 + 2 * np.sin(2 * np.pi * time_a / 12)
        
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
        time_days = np.linspace(0, 30, 100)
        cumulative_dose_mSv = np.cumsum(np.random.exponential(0.04, 100))
        
        total_dose_mSv = cumulative_dose_mSv[-1]
        
        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 6))
        
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
            'total_dose_mSv': float(total_dose_mSv)
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

@app.route('/api/real_time_data')
def real_time_data():
    """API для получения реальных данных в реальном времени"""
    try:
        # Симуляция реальных данных
        current_time = datetime.now()
        
        # Симуляция положения МКС
        orbital_phase = (current_time.hour % 1.5) / 1.5
        latitude = 51.6 * np.sin(2 * np.pi * orbital_phase)
        longitude = (current_time.hour * 15) % 360 - 180
        
        # Симуляция температуры
        is_sun_side = orbital_phase < 0.6
        internal_temp = 22 + np.random.normal(0, 0.5)
        external_temp = 40 + (121 - 40) * np.sin(np.pi * orbital_phase / 0.6) if is_sun_side else -157
        
        # Симуляция радиации
        base_radiation = 30
        radiation = base_radiation * (2 + 2 * np.random.rand()) if (current_time.minute % 10) < 3 else base_radiation
        
        # Симуляция орбитальных параметров
        altitude = 408.0 + np.random.normal(0, 0.1)
        speed = 27600 + np.random.normal(0, 100)
        
        real_time_data = {
            'timestamp': current_time.isoformat(),
            'position': {
                'latitude': float(latitude),
                'longitude': float(longitude)
            },
            'environment': {
                'internal_temp': float(internal_temp),
                'external_temp': float(external_temp),
                'radiation_uSv_h': float(radiation)
            },
            'orbital': {
                'altitude_km': float(altitude),
                'speed_kmh': float(speed),
                'orbital_period_min': 92.9
            }
        }
        
        return jsonify({
            'success': True,
            'data': real_time_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/trend_analysis')
def trend_analysis():
    """API для анализа трендов изменения параметров"""
    try:
        # Симуляция данных о трендах
        days = 30
        time_days = np.linspace(0, days, 100)
        
        # Тренд высоты орбиты (медленное снижение с коррекциями)
        altitude_trend = 408.0 - 0.05 * time_days + 0.5 * np.sin(2 * np.pi * time_days / 10)
        
        # Тренд температуры (сезонные изменения)
        temp_trend = 22 + 2 * np.sin(2 * np.pi * time_days / 365)
        
        # Тренд радиации (солнечный цикл)
        radiation_trend = 30 + 5 * np.sin(2 * np.pi * time_days / (365 * 5.5))
        
        # Создание графика
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # График высоты орбиты
        axes[0].plot(time_days, altitude_trend, 'b-', linewidth=2)
        axes[0].set_xlabel('Дни')
        axes[0].set_ylabel('Высота орбиты (км)')
        axes[0].set_title('Тренд изменения высоты орбиты МКС')
        axes[0].grid(True, alpha=0.3)
        
        # График температуры
        axes[1].plot(time_days, temp_trend, 'r-', linewidth=2)
        axes[1].set_xlabel('Дни')
        axes[1].set_ylabel('Температура (°C)')
        axes[1].set_title('Тренд изменения температуры на МКС')
        axes[1].grid(True, alpha=0.3)
        
        # График радиации
        axes[2].plot(time_days, radiation_trend, 'purple', linewidth=2)
        axes[2].set_xlabel('Дни')
        axes[2].set_ylabel('Радиация (мкЗв/час)')
        axes[2].set_title('Тренд изменения радиационного фона')
        axes[2].grid(True, alpha=0.3)
        
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

@app.route('/api/export/data')
def export_data():
    """API для экспорта данных в формате CSV"""
    try:
        # Получение параметров запроса
        data_type = request.args.get('type', 'orbital')
        
        # Создание CSV данных
        csv_data = "timestamp,parameter,value,unit\n"
        
        # Симуляция данных в зависимости от типа
        current_time = datetime.now()
        if data_type == 'orbital':
            csv_data += f"{current_time.isoformat()},altitude,408.0,km\n"
            csv_data += f"{current_time.isoformat()},speed,27600,km/h\n"
            csv_data += f"{current_time.isoformat()},period,92.9,min\n"
        elif data_type == 'environment':
            csv_data += f"{current_time.isoformat()},internal_temp,22,C\n"
            csv_data += f"{current_time.isoformat()},external_temp,121,C\n"
            csv_data += f"{current_time.isoformat()},radiation,30,uSv/h\n"
        elif data_type == 'position':
            csv_data += f"{current_time.isoformat()},latitude,51.6,degrees\n"
            csv_data += f"{current_time.isoformat()},longitude,-123.4,degrees\n"
        
        # Создание ответа с CSV данными
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=iss_{data_type}_data.csv'
        
        return response
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/export/report')
def export_report():
    """API для экспорта отчета в формате JSON"""
    try:
        # Симуляция данных отчета
        report_data = {
            "report_generated": datetime.now().isoformat(),
            "iss_telemetry_report": {
                "orbital_parameters": {
                    "altitude_km": 408.0,
                    "orbital_speed_kmh": 27600,
                    "orbital_period_min": 92.9,
                    "orbits_per_day": 15.5
                },
                "position_data": {
                    "latitude": 51.6,
                    "longitude": -123.4,
                    "timestamp": datetime.now().isoformat()
                },
                "environmental_conditions": {
                    "internal_temperature_c": 22,
                    "external_temperature_sun_c": 121,
                    "external_temperature_shadow_c": -157,
                    "radiation_level_uSv_h": 30
                },
                "radiation_analysis": {
                    "cumulative_dose_30_days_mSv": 1.2,
                    "annual_extrapolated_dose_mSv": 14.6
                }
            }
        }
        
        # Создание ответа с JSON данными
        response = make_response(json.dumps(report_data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = 'attachment; filename=iss_telemetry_report.json'
        
        return response
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)