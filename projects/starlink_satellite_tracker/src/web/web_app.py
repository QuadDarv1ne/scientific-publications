#!/usr/bin/env python3
"""
Web interface for Starlink Satellite Tracker
Provides a dashboard for visualizing satellite positions, passes, and coverage.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import logging
from functools import wraps
import hashlib

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our configuration manager
from utils.config_manager import get_config

# Import tracker module with error handling
try:
    from core.main import StarlinkTracker
    tracker_instance = StarlinkTracker()
    TRACKER_AVAILABLE = True
except ImportError:
    TRACKER_AVAILABLE = False
    # Create a minimal version
    class MinimalTracker:
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
        
        def start_scheduler(self):
            """Minimal scheduler method."""
            pass
        
        def clear_caches(self):
            """Minimal cache clearing method."""
            pass
    
    tracker_instance = MinimalTracker()

# Simple in-memory cache for API responses
class APICache:
    def __init__(self, default_ttl=300):  # 5 minutes default TTL
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)
    
    def get(self, key):
        """Retrieve cached data if not expired."""
        if key in self.cache:
            timestamp = self.timestamps[key]
            if (datetime.now() - timestamp).total_seconds() < self.default_ttl:
                self.logger.debug(f"Cache hit for key: {key}")
                return self.cache[key]
            else:
                # Remove expired entry
                del self.cache[key]
                del self.timestamps[key]
                self.logger.debug(f"Cache expired for key: {key}")
        return None
    
    def set(self, key, value):
        """Store data in cache."""
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
        self.logger.debug(f"Cached data for key: {key}")
    
    def clear(self):
        """Clear all cached data."""
        self.cache.clear()
        self.timestamps.clear()
        self.logger.debug("API cache cleared")

# Initialize cache
api_cache = APICache()

# Cache decorator for API endpoints
def cached(ttl=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f.__name__ + str(args) + str(sorted(kwargs.items()))
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            api_cache.set(cache_key, result)
            return result
        return wrapper
    return decorator

# Error handler decorator
def handle_api_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.error(f"API error in {f.__name__}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e) if app.config.get('DEBUG') else 'An error occurred'
            }), 500
    return wrapper

app = Flask(__name__)

# Load configuration
config = get_config()

# Set default observer location from config
if 'observer' in config:
    DEFAULT_LATITUDE = config['observer'].get('default_latitude', 55.7558)
    DEFAULT_LONGITUDE = config['observer'].get('default_longitude', 37.6173)
else:
    DEFAULT_LATITUDE = 55.7558  # Moscow
    DEFAULT_LONGITUDE = 37.6173

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Start scheduler for automated tasks (if available)
if TRACKER_AVAILABLE:
    try:
        # Try to start scheduler if method exists
        if hasattr(tracker_instance, 'start_scheduler'):
            try:
                tracker_instance.start_scheduler()
            except:
                pass  # Ignore scheduler errors
    except Exception as e:
        app.logger.warning(f"Could not start scheduler: {e}")

@app.route('/')
def index():
    """Main dashboard showing current satellite positions."""
    return render_template('index.html')

@app.route('/api/satellites')
@handle_api_errors
@cached(ttl=600)  # Cache for 10 minutes
def api_satellites():
    """API endpoint returning current satellite positions."""
    # Update TLE data if needed
    satellites = tracker_instance.update_tle_data()
    
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

@app.route('/passes')
def passes():
    """Page showing upcoming satellite passes."""
    return render_template('passes.html')

@app.route('/api/passes')
@handle_api_errors
@cached(ttl=300)  # Cache for 5 minutes
def api_passes():
    """API endpoint returning predicted satellite passes."""
    # Get location parameters from request or use defaults
    try:
        lat = float(request.args.get('lat', DEFAULT_LATITUDE))
        lon = float(request.args.get('lon', DEFAULT_LONGITUDE))
        hours = int(request.args.get('hours', 24))
        
        # Validate parameters
        if not (-90 <= lat <= 90):
            return jsonify({'error': 'Invalid latitude. Must be between -90 and 90.'}), 400
        if not (-180 <= lon <= 180):
            return jsonify({'error': 'Invalid longitude. Must be between -180 and 180.'}), 400
        if not (1 <= hours <= 168):  # Max 1 week
            return jsonify({'error': 'Invalid hours. Must be between 1 and 168.'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid parameter format.'}), 400
    
    # Predict passes
    passes = tracker_instance.predict_passes(lat, lon, hours_ahead=hours)
    
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

@app.route('/coverage')
def coverage():
    """Page showing global Starlink coverage."""
    return render_template('coverage.html')

@app.route('/api/coverage')
@handle_api_errors
@cached(ttl=3600)  # Cache for 1 hour
def api_coverage():
    """API endpoint returning global coverage data."""
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

@app.route('/settings')
def settings():
    """Page for configuring observer location and notification settings."""
    return render_template('settings.html')

@app.route('/export')
def export():
    """Page for exporting satellite data."""
    return render_template('export.html')

@app.route('/api/export/<format>')
@handle_api_errors
def api_export(format):
    """API endpoint for exporting data in various formats."""
    from utils.data_processor import DataProcessor
    
    # Initialize processor with config
    processor = DataProcessor()
    
    # Load satellite data
    satellites = processor.load_satellite_data()
    
    if not satellites:
        return jsonify({'error': 'No satellite data available'}), 404
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'starlink_export_{timestamp}'
    
    if format == 'json':
        # Export to JSON
        processor.export_to_json(satellites, filename + '.json')
        # Return the data
        with open(filename + '.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    elif format == 'csv':
        # Export to CSV
        processor.export_to_csv(satellites, filename + '.csv')
        # Return the data
        import pandas as pd
        df = pd.read_csv(filename + '.csv')
        csv_data = df.to_csv(index=False)
        return csv_data, 200, {'Content-Type': 'text/csv'}
    else:
        return jsonify({'error': f'Unsupported format: {format}'}), 400

@app.route('/api/cache/clear', methods=['POST'])
@handle_api_errors
def clear_cache():
    """API endpoint to clear the cache."""
    api_cache.clear()
    # Try to clear tracker caches if method exists
    if hasattr(tracker_instance, 'clear_caches'):
        try:
            tracker_instance.clear_caches()
        except:
            pass  # Ignore errors when clearing tracker caches
    return jsonify({'message': 'Cache cleared successfully'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

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
    
    with open(os.path.join(templates_dir, 'base.html'), 'w', encoding='utf-8') as f:
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
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
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
    
    with open(os.path.join(templates_dir, 'passes.html'), 'w', encoding='utf-8') as f:
        f.write(passes_html)
    
    # Create simple templates for other pages
    simple_pages = {
        'coverage.html': '<h1>Global Coverage Map</h1><p>Interactive map showing Starlink coverage worldwide.</p>',
        'settings.html': '<h1>Settings</h1><p>Configure your observation location and notification preferences.</p>',
        'export.html': '<h1>Data Export</h1><p>Export satellite data in various formats.</p>'
    }
    
    for filename, content in simple_pages.items():
        with open(os.path.join(templates_dir, filename), 'w', encoding='utf-8') as f:
            f.write('{% extends "base.html" %}\n\n{% block content %}\n' + content + '\n{% endblock %}')

if __name__ == '__main__':
    # Create templates directory
    create_templates_dir()
    
    # Run the web application
    app.run(debug=True, host='0.0.0.0', port=5000)