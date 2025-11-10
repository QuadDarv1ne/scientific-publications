#!/usr/bin/env python3
"""
Web interface for Starlink Satellite Tracker
Provides a dashboard for visualizing satellite positions, passes, and coverage.
"""

import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request

# Import our tracker module
try:
    from main import StarlinkTracker
except ImportError:
    # If main.py doesn't exist, create a minimal version
    class StarlinkTracker:
        def __init__(self):
            pass
        
        def update_tle_data(self, force=False):
            return []
        
        def predict_passes(self, latitude, longitude, altitude=0, hours_ahead=24, min_elevation=10):
            # Return sample data
            return [
                {
                    'satellite': 'STARLINK-1234',
                    'time': datetime.now() + timedelta(minutes=30),
                    'altitude': 65.5,
                    'azimuth': 42.3,
                    'distance': 350.2
                },
                {
                    'satellite': 'STARLINK-5678',
                    'time': datetime.now() + timedelta(minutes=90),
                    'altitude': 78.2,
                    'azimuth': 58.1,
                    'distance': 420.7
                }
            ]

app = Flask(__name__)

# Global tracker instance
tracker = StarlinkTracker()

# Default observer location (can be configured)
DEFAULT_LATITUDE = 55.7558  # Moscow
DEFAULT_LONGITUDE = 37.6173

@app.route('/')
def index():
    """Main dashboard showing current satellite positions."""
    return render_template('index.html')

@app.route('/api/satellites')
def api_satellites():
    """API endpoint returning current satellite positions."""
    try:
        # Update TLE data if needed
        satellites = tracker.update_tle_data()
        
        # Return simplified satellite data
        sat_data = []
        for sat in satellites[:20]:  # Limit to first 20 for performance
            sat_data.append({
                'name': sat.name,
                'id': sat.name.split('-')[-1] if '-' in sat.name else sat.name
            })
        
        return jsonify({
            'satellites': sat_data,
            'count': len(sat_data),
            'updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/passes')
def passes():
    """Page showing upcoming satellite passes."""
    return render_template('passes.html')

@app.route('/api/passes')
def api_passes():
    """API endpoint returning predicted satellite passes."""
    try:
        # Get location parameters from request or use defaults
        lat = float(request.args.get('lat', DEFAULT_LATITUDE))
        lon = float(request.args.get('lon', DEFAULT_LONGITUDE))
        hours = int(request.args.get('hours', 24))
        
        # Predict passes
        passes = tracker.predict_passes(lat, lon, hours_ahead=hours)
        
        # Format for JSON serialization
        formatted_passes = []
        for p in passes:
            formatted_passes.append({
                'satellite': p['satellite'],
                'time': p['time'].isoformat(),
                'altitude': round(p['altitude'], 1),
                'azimuth': round(p['azimuth'], 1),
                'distance': round(p['distance'], 1)
            })
        
        return jsonify({
            'passes': formatted_passes,
            'count': len(formatted_passes),
            'location': {'latitude': lat, 'longitude': lon},
            'period_hours': hours
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coverage')
def coverage():
    """Page showing global Starlink coverage."""
    return render_template('coverage.html')

@app.route('/api/coverage')
def api_coverage():
    """API endpoint returning global coverage data."""
    try:
        # In a real implementation, this would calculate coverage polygons
        # For now, return sample data
        coverage_data = {
            'regions': [
                {
                    'name': 'North America',
                    'satellite_count': 1500,
                    'coverage_percentage': 98.5
                },
                {
                    'name': 'Europe',
                    'satellite_count': 800,
                    'coverage_percentage': 95.2
                },
                {
                    'name': 'Asia',
                    'satellite_count': 750,
                    'coverage_percentage': 87.3
                }
            ],
            'total_satellites': 2500,
            'global_coverage': 92.1
        }
        
        return jsonify(coverage_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings():
    """Page for configuring observer location and notification settings."""
    return render_template('settings.html')

@app.route('/export')
def export():
    """Page for exporting satellite data."""
    return render_template('export.html')

@app.route('/api/export/<format>')
def api_export(format):
    """API endpoint for exporting data in various formats."""
    try:
        # This would implement actual data export
        # For now, just return sample data
        data = {
            'generated': datetime.now().isoformat(),
            'satellite_count': 100,
            'format': format
        }
        
        if format == 'json':
            return jsonify(data)
        elif format == 'csv':
            # Would return CSV data
            csv_data = "name,id,altitude,velocity\n"
            csv_data += "STARLINK-1234,1234,550,7.5\n"
            csv_data += "STARLINK-5678,5678,545,7.6\n"
            return csv_data, 200, {'Content-Type': 'text/csv'}
        else:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_templates_dir():
    """Create templates directory with basic HTML files."""
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create base template
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Starlink Satellite Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">🛰️ Starlink Tracker</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/passes">Passes</a>
                <a class="nav-link" href="/coverage">Coverage</a>
                <a class="nav-link" href="/settings">Settings</a>
                <a class="nav-link" href="/export">Export</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_html)
    
    # Create index template
    index_html = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Starlink Satellite Tracker Dashboard</h1>
        <p class="lead">Real-time tracking of SpaceX Starlink satellites</p>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                Current Status
            </div>
            <div class="card-body">
                <p>Loading satellite data...</p>
                <div id="satellite-count">-</div>
                <div id="last-update">-</div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                Next Pass
            </div>
            <div class="card-body">
                <p>Calculating next satellite pass...</p>
                <div id="next-pass">-</div>
            </div>
        </div>
    </div>
</div>

<script>
// Fetch satellite data
fetch('/api/satellites')
    .then(response => response.json())
    .then(data => {
        document.getElementById('satellite-count').innerHTML = 
            `<strong>Satellites Tracked:</strong> ${data.count}`;
        document.getElementById('last-update').innerHTML = 
            `<strong>Last Updated:</strong> ${new Date(data.updated).toLocaleString()}`;
    })
    .catch(error => {
        console.error('Error fetching satellite data:', error);
    });

// Fetch next pass
fetch('/api/passes?hours=24')
    .then(response => response.json())
    .then(data => {
        if (data.passes && data.passes.length > 0) {
            const nextPass = data.passes[0];
            document.getElementById('next-pass').innerHTML = 
                `<strong>${nextPass.satellite}</strong><br>
                ${new Date(nextPass.time).toLocaleString()}<br>
                Altitude: ${nextPass.altitude}°`;
        } else {
            document.getElementById('next-pass').innerHTML = 'No passes found';
        }
    })
    .catch(error => {
        console.error('Error fetching pass data:', error);
    });
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    
    # Create passes template
    passes_html = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Upcoming Satellite Passes</h1>
        <p>Predicted passes over your location</p>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Satellite</th>
                    <th>Date & Time</th>
                    <th>Altitude</th>
                    <th>Azimuth</th>
                    <th>Distance (km)</th>
                </tr>
            </thead>
            <tbody id="passes-table">
                <tr><td colspan="5">Loading passes...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<script>
// Fetch passes data
fetch('/api/passes?hours=48')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('passes-table');
        tableBody.innerHTML = '';
        
        if (data.passes && data.passes.length > 0) {
            data.passes.forEach(pass => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${pass.satellite}</td>
                    <td>${new Date(pass.time).toLocaleString()}</td>
                    <td>${pass.altitude}°</td>
                    <td>${pass.azimuth}°</td>
                    <td>${pass.distance}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="5">No passes found</td></tr>';
        }
    })
    .catch(error => {
        console.error('Error fetching passes data:', error);
        document.getElementById('passes-table').innerHTML = 
            '<tr><td colspan="5">Error loading passes</td></tr>';
    });
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'passes.html'), 'w') as f:
        f.write(passes_html)
    
    # Create simple templates for other pages
    simple_pages = {
        'coverage.html': '<h1>Global Coverage Map</h1><p>Interactive map showing Starlink coverage worldwide.</p>',
        'settings.html': '<h1>Settings</h1><p>Configure your observation location and notification preferences.</p>',
        'export.html': '<h1>Data Export</h1><p>Export satellite data in various formats.</p>'
    }
    
    for filename, content in simple_pages.items():
        with open(os.path.join(templates_dir, filename), 'w') as f:
            f.write('{% extends "base.html" %}\n\n{% block content %}\n' + content + '\n{% endblock %}')

if __name__ == '__main__':
    # Create templates directory
    create_templates_dir()
    
    # Run the web application
    app.run(debug=True, host='0.0.0.0', port=5000)