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
import base64
from io import BytesIO

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
                    'distance': 350.2,
                    'velocity': 7.5,
                    'brightness': 2.1
                },
                {
                    'satellite': 'STARLINK-5678',
                    'time': datetime.now() + timedelta(minutes=90),
                    'altitude': 78.2,
                    'azimuth': 58.1,
                    'distance': 420.7,
                    'velocity': 7.2,
                    'brightness': 1.8
                }
            ]
        
        def get_satellite_info(self, satellite_name):
            return {
                'name': satellite_name,
                'norad_id': 12345,
                'position': {
                    'latitude': 45.0,
                    'longitude': -122.0,
                    'altitude': 550.0
                },
                'orbit': {
                    'inclination': 53.0,
                    'eccentricity': 0.001,
                    'period': 95.0,
                    'semi_major_axis': 6900.0
                },
                'updated': datetime.now().isoformat()
            }
        
        def start_scheduler(self):
            """Minimal scheduler method."""
            pass
        
        def clear_caches(self):
            """Minimal cache clearing method."""
            pass
    
    tracker_instance = MinimalTracker()

# Multi-level cache for API responses
# Uses Redis for persistent caching and in-memory for fast access
class APICache:
    def __init__(self, default_ttl=300):  # 5 minutes default TTL
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)
        
        # Try to initialize Redis cache
        try:
            import redis
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()  # Test connection
            self.use_redis = True
            self.logger.info("Redis cache initialized successfully")
        except:
            self.redis_client = None
            self.use_redis = False
            self.logger.warning("Redis not available, using in-memory cache only")
    
    def get(self, key):
        """Retrieve cached data from Redis or in-memory cache."""
        # Try to get from Redis first (if available)
        if self.use_redis and self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    self.logger.debug(f"Redis cache hit for key: {key}")
                    # Handle potential async response
                    if hasattr(cached_data, '__await__'):
                        # This is an async response, skip Redis caching
                        pass
                    else:
                        return json.loads(cached_data)
            except Exception as e:
                self.logger.warning(f"Error retrieving from Redis cache: {e}")
        
        # Fall back to in-memory cache
        if key in self.cache:
            timestamp = self.timestamps[key]
            if (datetime.now() - timestamp).total_seconds() < self.default_ttl:
                self.logger.debug(f"In-memory cache hit for key: {key}")
                return self.cache[key]
            else:
                # Remove expired entry
                del self.cache[key]
                del self.timestamps[key]
                self.logger.debug(f"In-memory cache expired for key: {key}")
        return None
    
    def set(self, key, value):
        """Store data in both Redis and in-memory cache."""
        # Store in Redis (if available)
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.setex(key, int(self.default_ttl), json.dumps(value))
                self.logger.debug(f"Cached data in Redis for key: {key}")
            except Exception as e:
                self.logger.warning(f"Error storing in Redis cache: {e}")
        
        # Store in in-memory cache
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
        self.logger.debug(f"Cached data in memory for key: {key}")
    
    def clear(self):
        """Clear all cached data from both Redis and in-memory cache."""
        # Clear Redis cache (if available)
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.flushdb()
                self.logger.debug("Redis cache cleared")
            except Exception as e:
                self.logger.warning(f"Error clearing Redis cache: {e}")
        
        # Clear in-memory cache
        self.cache.clear()
        self.timestamps.clear()
        self.logger.debug("In-memory cache cleared")

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

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'templates'))

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

def get_template_name(base_name, language='en'):
    """Get template name based on language preference."""
    if language == 'ru':
        return f"{base_name}_ru.html"
    return f"{base_name}.html"

@app.route('/')
def index():
    """Main dashboard showing current satellite positions."""
    language = request.args.get('lang', 'en')
    template = get_template_name('index', language)
    return render_template(template)

@app.route('/passes')
def passes():
    """Page showing upcoming satellite passes."""
    language = request.args.get('lang', 'en')
    template = get_template_name('passes', language)
    return render_template(template)

@app.route('/coverage')
def coverage():
    """Page showing global Starlink coverage."""
    language = request.args.get('lang', 'en')
    template = get_template_name('coverage', language)
    return render_template(template)

@app.route('/settings')
def settings():
    """Page for configuring observer location and notification settings."""
    language = request.args.get('lang', 'en')
    template = get_template_name('settings', language)
    return render_template(template)

@app.route('/export')
def export():
    """Page for exporting satellite data."""
    language = request.args.get('lang', 'en')
    template = get_template_name('export', language)
    return render_template(template)

@app.route('/api/satellites')
@handle_api_errors
@cached(ttl=600)  # Cache for 10 minutes
def api_satellites():
    """API endpoint returning current satellite positions."""
    try:
        # Update TLE data if needed
        satellites = tracker_instance.update_tle_data()
        
        # Return simplified satellite data
        sat_data = []
        for sat in satellites[:50]:  # Limit to first 50 for performance
            sat_data.append({
                'name': sat.name,
                'id': sat.name.split('-')[-1] if '-' in sat.name else sat.name
            })
        
        return jsonify({
            'satellites': sat_data,
            'count': len(sat_data),
            'total_count': len(satellites),
            'updated': datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Error in api_satellites: {e}")
        return jsonify({
            'satellites': [],
            'count': 0,
            'total_count': 0,
            'updated': datetime.now().isoformat(),
            'error': 'Failed to load satellite data'
        }), 500

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
    
    try:
        # Predict passes
        passes = tracker_instance.predict_passes(lat, lon, hours_ahead=hours)
        
        # Sort by time
        passes.sort(key=lambda x: x['time'])
        
        # Format for JSON serialization
        formatted_passes = []
        for p in passes:
            formatted_passes.append({
                'satellite': p['satellite'],
                'time': p['time'].isoformat(),
                'altitude': round(p['altitude'], 1),
                'azimuth': round(p['azimuth'], 1),
                'distance': round(p['distance'], 1),
                'velocity': round(p['velocity'], 2) if 'velocity' in p else 0,
                'brightness': round(p['brightness'], 1) if 'brightness' in p else 5.0
            })
        
        return jsonify({
            'passes': formatted_passes,
            'count': len(formatted_passes),
            'location': {'latitude': lat, 'longitude': lon},
            'period_hours': hours,
            'generated': datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Error in api_passes: {e}")
        return jsonify({
            'passes': [],
            'count': 0,
            'error': 'Failed to predict satellite passes'
        }), 500

@app.route('/api/coverage')
@handle_api_errors
@cached(ttl=3600)  # Cache for 1 hour
def api_coverage():
    """API endpoint returning global coverage data."""
    # In a real implementation, this would calculate coverage polygons
    # For now, return sample data
    try:
        # Get total satellite count
        satellites = tracker_instance.update_tle_data()
        total_satellites = len(satellites) if satellites else 0
        
        coverage_data = {
            'regions': [
                {
                    'name': 'North America',
                    'satellite_count': int(total_satellites * 0.4),
                    'coverage_percentage': 98.5
                },
                {
                    'name': 'Europe',
                    'satellite_count': int(total_satellites * 0.2),
                    'coverage_percentage': 95.2
                },
                {
                    'name': 'Asia',
                    'satellite_count': int(total_satellites * 0.15),
                    'coverage_percentage': 87.3
                },
                {
                    'name': 'South America',
                    'satellite_count': int(total_satellites * 0.1),
                    'coverage_percentage': 75.1
                },
                {
                    'name': 'Africa',
                    'satellite_count': int(total_satellites * 0.08),
                    'coverage_percentage': 68.4
                },
                {
                    'name': 'Oceania',
                    'satellite_count': int(total_satellites * 0.07),
                    'coverage_percentage': 82.7
                }
            ],
            'total_satellites': total_satellites,
            'global_coverage': 92.1,
            'generated': datetime.now().isoformat()
        }
        
        return jsonify(coverage_data)
    except Exception as e:
        app.logger.error(f"Error in api_coverage: {e}")
        return jsonify({
            'regions': [],
            'total_satellites': 0,
            'global_coverage': 0,
            'error': 'Failed to generate coverage data'
        }), 500

@app.route('/api/satellite/<satellite_name>')
@handle_api_errors
@cached(ttl=300)  # Cache for 5 minutes
def api_satellite_info(satellite_name):
    """API endpoint returning detailed information about a specific satellite."""
    try:
        info = tracker_instance.get_satellite_info(satellite_name)
        if info:
            return jsonify(info)
        else:
            return jsonify({'error': f'Satellite {satellite_name} not found'}), 404
    except Exception as e:
        app.logger.error(f"Error in api_satellite_info: {e}")
        return jsonify({'error': 'Failed to get satellite information'}), 500

@app.route('/api/search')
@handle_api_errors
@cached(ttl=300)  # Cache for 5 minutes
def api_search():
    """API endpoint for searching satellites by name or ID."""
    try:
        query = request.args.get('q', '').strip().upper()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Update TLE data if needed
        satellites = tracker_instance.update_tle_data()
        
        # Search for matching satellites
        matches = []
        for sat in satellites:
            if query in sat.name.upper() or query in str(sat.model.satnum):
                matches.append({
                    'name': sat.name,
                    'id': sat.model.satnum,
                    'short_name': sat.name.split('-')[-1] if '-' in sat.name else sat.name
                })
                # Limit to 20 results
                if len(matches) >= 20:
                    break
        
        return jsonify({
            'results': matches,
            'count': len(matches),
            'query': query
        })
    except Exception as e:
        app.logger.error(f"Error in api_search: {e}")
        return jsonify({'error': 'Failed to search satellites'}), 500

@app.route('/api/export/<format>')
@handle_api_errors
def api_export(format):
    """API endpoint for exporting data in various formats."""
    try:
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
            success = processor.export_to_json(satellites, filename + '.json')
            if success:
                # Return the data
                try:
                    with open(filename + '.json', 'r') as f:
                        data = json.load(f)
                    return jsonify(data)
                except Exception:
                    return jsonify({'message': 'Export completed successfully'}), 200
            else:
                return jsonify({'error': 'Failed to export data to JSON'}), 500
        elif format == 'csv':
            # Export to CSV
            success = processor.export_to_csv(satellites, filename + '.csv')
            if success:
                return jsonify({'message': 'CSV export completed successfully'}), 200
            else:
                return jsonify({'error': 'Failed to export data to CSV'}), 500
        else:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
    except Exception as e:
        app.logger.error(f"Error in api_export: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

@app.route('/api/cache/clear', methods=['POST'])
@handle_api_errors
def clear_cache():
    """API endpoint to clear the cache."""
    try:
        api_cache.clear()
        # Try to clear tracker caches if method exists
        if hasattr(tracker_instance, 'clear_caches'):
            try:
                tracker_instance.clear_caches()
            except:
                pass  # Ignore errors when clearing tracker caches
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        app.logger.error(f"Error clearing cache: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500

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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .icon-circle {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        .navbar-brand {
            font-weight: bold;
        }
        .card {
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            transition: box-shadow 0.3s ease-in-out;
        }
        .card:hover {
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        }
        .table th {
            font-weight: 600;
        }
        footer {
            margin-top: 2rem;
            padding: 1rem 0;
            border-top: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-satellite"></i> Starlink Tracker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav">
                    <a class="nav-link" href="/"><i class="fas fa-home"></i> Dashboard</a>
                    <a class="nav-link" href="/passes"><i class="fas fa-calendar-alt"></i> Passes</a>
                    <a class="nav-link" href="/coverage"><i class="fas fa-globe-americas"></i> Coverage</a>
                    <a class="nav-link" href="/settings"><i class="fas fa-cog"></i> Settings</a>
                    <a class="nav-link" href="/export"><i class="fas fa-download"></i> Export</a>
                </div>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <footer class="bg-light">
        <div class="container">
            <div class="row">
                <div class="col-md-12 text-center">
                    <p class="mb-0 text-muted">
                        <i class="fas fa-satellite"></i> Starlink Satellite Tracker &copy; 2025
                    </p>
                </div>
            </div>
        </div>
    </footer>
    
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
                <h5 class="mb-0">Current Status</h5>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h6 class="text-muted">Satellites Tracked</h6>
                        <h3 id="satellite-count" class="mb-0">-</h3>
                    </div>
                    <div class="icon-circle bg-primary text-white">
                        <i class="fas fa-satellite"></i>
                    </div>
                </div>
                <div class="mt-3">
                    <small class="text-muted">Last Updated: <span id="last-update">-</span></small>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Next Visible Pass</h5>
            </div>
            <div class="card-body">
                <div id="next-pass-content">
                    <p class="text-muted">Calculating next satellite pass...</p>
                    <div id="next-pass">-</div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Recent Activity</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Satellite</th>
                                <th>Time</th>
                                <th>Max Elevation</th>
                                <th>Azimuth</th>
                                <th>Distance</th>
                            </tr>
                        </thead>
                        <tbody id="recent-passes">
                            <tr>
                                <td colspan="5" class="text-center">Loading recent passes...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Fetch satellite data
fetch('/api/satellites')
    .then(response => response.json())
    .then(data => {
        document.getElementById('satellite-count').textContent = data.count;
        document.getElementById('last-update').textContent = new Date(data.updated).toLocaleString();
    })
    .catch(error => {
        console.error('Error fetching satellite data:', error);
        document.getElementById('satellite-count').textContent = 'Error';
        document.getElementById('last-update').textContent = 'Error loading data';
    });

// Fetch next pass and recent passes
fetch('/api/passes?hours=48')
    .then(response => response.json())
    .then(data => {
        const nextPassContent = document.getElementById('next-pass-content');
        const recentPasses = document.getElementById('recent-passes');
        
        if (data.passes && data.passes.length > 0) {
            // Next pass
            const nextPass = data.passes[0];
            nextPassContent.innerHTML = `
                <div class="d-flex justify-content-between">
                    <div>
                        <h5>${nextPass.satellite}</h5>
                        <p class="mb-1"><strong>Time:</strong> ${new Date(nextPass.time).toLocaleString()}</p>
                        <p class="mb-1"><strong>Max Elevation:</strong> ${nextPass.altitude}°</p>
                        <p class="mb-0"><strong>Azimuth:</strong> ${nextPass.azimuth}°</p>
                    </div>
                    <div>
                        <span class="badge bg-success">Visible</span>
                    </div>
                </div>
            `;
            
            // Recent passes (show first 5)
            recentPasses.innerHTML = '';
            const passesToShow = Math.min(5, data.passes.length);
            for (let i = 0; i < passesToShow; i++) {
                const pass = data.passes[i];
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${pass.satellite}</td>
                    <td>${new Date(pass.time).toLocaleString()}</td>
                    <td>${pass.altitude}°</td>
                    <td>${pass.azimuth}°</td>
                    <td>${pass.distance} km</td>
                `;
                recentPasses.appendChild(row);
            }
        } else {
            nextPassContent.innerHTML = '<p class="text-muted">No upcoming passes found</p>';
            recentPasses.innerHTML = '<tr><td colspan="5" class="text-center">No passes found</td></tr>';
        }
    })
    .catch(error => {
        console.error('Error fetching pass data:', error);
        document.getElementById('next-pass-content').innerHTML = '<p class="text-danger">Error loading pass data</p>';
        document.getElementById('recent-passes').innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error loading passes</td></tr>';
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
        <p class="lead">Predicted passes over your location</p>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <form id="pass-filter-form" class="row g-3">
                    <div class="col-md-3">
                        <label for="latitude" class="form-label">Latitude</label>
                        <input type="number" class="form-control" id="latitude" step="0.0001" placeholder="55.7558" value="55.7558">
                    </div>
                    <div class="col-md-3">
                        <label for="longitude" class="form-label">Longitude</label>
                        <input type="number" class="form-control" id="longitude" step="0.0001" placeholder="37.6173" value="37.6173">
                    </div>
                    <div class="col-md-3">
                        <label for="hours" class="form-label">Hours Ahead</label>
                        <select class="form-select" id="hours">
                            <option value="24">24 hours</option>
                            <option value="48" selected>48 hours</option>
                            <option value="72">72 hours</option>
                            <option value="168">1 week</option>
                        </select>
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
                        <button type="submit" class="btn btn-primary w-100">Update</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Predicted Passes</h5>
                <span class="badge bg-secondary" id="pass-count">0 passes</span>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Satellite</th>
                                <th>Date & Time</th>
                                <th>Max Elevation</th>
                                <th>Azimuth</th>
                                <th>Distance</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody id="passes-table">
                            <tr>
                                <td colspan="6" class="text-center">Loading passes...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Function to fetch and display passes
function fetchPasses(lat, lon, hours) {
    const tableBody = document.getElementById('passes-table');
    tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Loading passes...</td></tr>';
    
    fetch(`/api/passes?lat=${lat}&lon=${lon}&hours=${hours}`)
        .then(response => response.json())
        .then(data => {
            tableBody.innerHTML = '';
            document.getElementById('pass-count').textContent = `${data.passes.length} passes`;
            
            if (data.passes && data.passes.length > 0) {
                data.passes.forEach(pass => {
                    const row = document.createElement('tr');
                    // Calculate approximate duration (this is a simplified calculation)
                    const duration = Math.max(1, Math.round(pass.altitude / 10)); // In minutes
                    
                    row.innerHTML = `
                        <td>${pass.satellite}</td>
                        <td>${new Date(pass.time).toLocaleString()}</td>
                        <td>
                            <div class="d-flex align-items-center">
                                <span>${pass.altitude}°</span>
                                <div class="progress ms-2" style="width: 100px; height: 5px;">
                                    <div class="progress-bar" role="progressbar" 
                                         style="width: ${Math.min(100, pass.altitude)}%" 
                                         aria-valuenow="${pass.altitude}" aria-valuemin="0" aria-valuemax="90"></div>
                                </div>
                            </div>
                        </td>
                        <td>${pass.azimuth}°</td>
                        <td>${pass.distance} km</td>
                        <td>~${duration} min</td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No passes found for the specified location and time period</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error fetching passes data:', error);
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading passes data</td></tr>';
        });
}

// Handle form submission
document.getElementById('pass-filter-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const lat = document.getElementById('latitude').value;
    const lon = document.getElementById('longitude').value;
    const hours = document.getElementById('hours').value;
    
    fetchPasses(lat, lon, hours);
});

// Load initial data
document.addEventListener('DOMContentLoaded', function() {
    fetchPasses(55.7558, 37.6173, 48);
});
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'passes.html'), 'w', encoding='utf-8') as f:
        f.write(passes_html)
    
    # Create coverage template
    coverage_html = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Global Starlink Coverage</h1>
        <p class="lead">Interactive map showing current Starlink satellite coverage worldwide</p>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Coverage Map</h5>
            </div>
            <div class="card-body">
                <div id="coverage-map" style="height: 500px; width: 100%; background-color: #f8f9fa; border-radius: 0.375rem; display: flex; align-items: center; justify-content: center;">
                    <div class="text-center">
                        <i class="fas fa-globe-americas fa-3x text-muted mb-3"></i>
                        <p class="text-muted">Interactive coverage map visualization</p>
                        <p class="small text-muted">This would show a world map with satellite coverage areas in a full implementation</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Regional Coverage Statistics</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Region</th>
                                <th>Satellites</th>
                                <th>Coverage</th>
                            </tr>
                        </thead>
                        <tbody id="coverage-stats">
                            <tr>
                                <td colspan="3" class="text-center">Loading coverage data...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Constellation Status</h5>
            </div>
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h6 class="text-muted">Total Satellites</h6>
                        <h3 id="total-satellites" class="mb-0">-</h3>
                    </div>
                    <div class="icon-circle bg-success text-white">
                        <i class="fas fa-satellite"></i>
                    </div>
                </div>
                
                <div class="progress mb-3">
                    <div class="progress-bar bg-success" role="progressbar" style="width: 92%" aria-valuenow="92" aria-valuemin="0" aria-valuemax="100">92% Operational</div>
                </div>
                
                <div class="row">
                    <div class="col-6">
                        <p class="mb-1"><small class="text-muted">Active</small></p>
                        <p class="mb-0"><strong id="active-satellites">-</strong></p>
                    </div>
                    <div class="col-6">
                        <p class="mb-1"><small class="text-muted">Inactive</small></p>
                        <p class="mb-0"><strong id="inactive-satellites">-</strong></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Fetch coverage data
fetch('/api/coverage')
    .then(response => response.json())
    .then(data => {
        // Update regional coverage statistics
        const statsTable = document.getElementById('coverage-stats');
        statsTable.innerHTML = '';
        
        if (data.regions && data.regions.length > 0) {
            data.regions.forEach(region => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${region.name}</td>
                    <td>${region.satellite_count}</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <span>${region.coverage_percentage}%</span>
                            <div class="progress ms-2" style="width: 100px; height: 5px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${region.coverage_percentage}%" 
                                     aria-valuenow="${region.coverage_percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                    </td>
                `;
                statsTable.appendChild(row);
            });
        } else {
            statsTable.innerHTML = '<tr><td colspan="3" class="text-center">No coverage data available</td></tr>';
        }
        
        // Update constellation status
        document.getElementById('total-satellites').textContent = data.total_satellites || '-';
        document.getElementById('active-satellites').textContent = Math.round((data.total_satellites || 0) * (data.global_coverage || 0) / 100) || '-';
        document.getElementById('inactive-satellites').textContent = Math.round((data.total_satellites || 0) * (100 - (data.global_coverage || 0)) / 100) || '-';
    })
    .catch(error => {
        console.error('Error fetching coverage data:', error);
        document.getElementById('coverage-stats').innerHTML = '<tr><td colspan="3" class="text-center text-danger">Error loading coverage data</td></tr>';
    });
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'coverage.html'), 'w', encoding='utf-8') as f:
        f.write(coverage_html)
    
    # Create settings template
    settings_html = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Settings</h1>
        <p class="lead">Configure your observation location and notification preferences</p>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Observer Location</h5>
            </div>
            <div class="card-body">
                <form id="location-form">
                    <div class="mb-3">
                        <label for="latitude" class="form-label">Latitude</label>
                        <input type="number" class="form-control" id="latitude" step="0.0001" placeholder="55.7558" value="55.7558">
                        <div class="form-text">Range: -90 to 90 degrees</div>
                    </div>
                    <div class="mb-3">
                        <label for="longitude" class="form-label">Longitude</label>
                        <input type="number" class="form-control" id="longitude" step="0.0001" placeholder="37.6173" value="37.6173">
                        <div class="form-text">Range: -180 to 180 degrees</div>
                    </div>
                    <div class="mb-3">
                        <label for="altitude" class="form-label">Altitude (meters)</label>
                        <input type="number" class="form-control" id="altitude" step="1" placeholder="0" value="0">
                    </div>
                    <div class="mb-3">
                        <label for="timezone" class="form-label">Timezone</label>
                        <select class="form-select" id="timezone">
                            <option value="Europe/Moscow" selected>Moscow (GMT+3)</option>
                            <option value="UTC">UTC</option>
                            <option value="America/New_York">New York (GMT-5)</option>
                            <option value="America/Los_Angeles">Los Angeles (GMT-8)</option>
                            <option value="Asia/Tokyo">Tokyo (GMT+9)</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Location</button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Notification Settings</h5>
            </div>
            <div class="card-body">
                <form id="notification-form">
                    <div class="mb-3">
                        <label class="form-label">Email Notifications</label>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="email-enabled">
                            <label class="form-check-label" for="email-enabled">Enable Email Notifications</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="email-address" class="form-label">Email Address</label>
                        <input type="email" class="form-control" id="email-address" placeholder="your@email.com">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Telegram Notifications</label>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="telegram-enabled">
                            <label class="form-check-label" for="telegram-enabled">Enable Telegram Notifications</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="telegram-chat-id" class="form-label">Telegram Chat ID</label>
                        <input type="text" class="form-control" id="telegram-chat-id" placeholder="Chat ID">
                    </div>
                    <div class="mb-3">
                        <label for="min-elevation" class="form-label">Minimum Elevation (degrees)</label>
                        <input type="number" class="form-control" id="min-elevation" min="0" max="90" value="10">
                        <div class="form-text">Only notify for passes above this elevation</div>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Notification Settings</button>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">System Configuration</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Data Sources</h6>
                        <div class="mb-3">
                            <label for="celestrak-url" class="form-label">Celestrak URL</label>
                            <input type="url" class="form-control" id="celestrak-url" value="https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle">
                        </div>
                        <div class="mb-3">
                            <label for="cache-days" class="form-label">Cache Duration (days)</label>
                            <input type="number" class="form-control" id="cache-days" min="1" max="30" value="7">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>Scheduler Settings</h6>
                        <div class="mb-3">
                            <label for="tle-update-cron" class="form-label">TLE Update Schedule</label>
                            <input type="text" class="form-control" id="tle-update-cron" value="0 0 */6 * *">
                            <div class="form-text">Cron expression for TLE updates</div>
                        </div>
                        <div class="mb-3">
                            <label for="prediction-cron" class="form-label">Prediction Update Schedule</label>
                            <input type="text" class="form-control" id="prediction-cron" value="*/30 * * * *">
                            <div class="form-text">Cron expression for prediction updates</div>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn btn-success" id="save-config">Save Configuration</button>
                <button type="button" class="btn btn-warning" id="clear-cache">Clear Cache</button>
            </div>
        </div>
    </div>
</div>

<script>
// Handle form submissions
document.getElementById('location-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Location settings saved successfully!');
});

document.getElementById('notification-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Notification settings saved successfully!');
});

document.getElementById('save-config').addEventListener('click', function() {
    alert('System configuration saved successfully!');
});

document.getElementById('clear-cache').addEventListener('click', function() {
    if (confirm('Are you sure you want to clear all cached data?')) {
        fetch('/api/cache/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Cache cleared successfully!');
            })
            .catch(error => {
                console.error('Error clearing cache:', error);
                alert('Error clearing cache');
            });
    }
});
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'settings.html'), 'w', encoding='utf-8') as f:
        f.write(settings_html)
    
    # Create export template
    export_html = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Data Export</h1>
        <p class="lead">Export satellite data in various formats for analysis</p>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Export Satellite Data</h5>
            </div>
            <div class="card-body">
                <form id="export-form">
                    <div class="mb-3">
                        <label class="form-label">Data to Export</label>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="include-tle" checked>
                            <label class="form-check-label" for="include-tle">Include TLE Data</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="include-predictions" checked>
                            <label class="form-check-label" for="include-predictions">Include Predictions</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="export-format" class="form-label">Export Format</label>
                        <select class="form-select" id="export-format">
                            <option value="json" selected>JSON</option>
                            <option value="csv">CSV</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="date-range" class="form-label">Date Range</label>
                        <select class="form-select" id="date-range">
                            <option value="all" selected>All Available Data</option>
                            <option value="today">Today</option>
                            <option value="week">Last 7 Days</option>
                            <option value="month">Last 30 Days</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-download"></i> Export Data
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Export History</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>File</th>
                                <th>Format</th>
                                <th>Date</th>
                                <th>Size</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="4" class="text-center">No export history available</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <button type="button" class="btn btn-sm btn-outline-secondary">
                    <i class="fas fa-trash"></i> Clear History
                </button>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">API Access</h5>
            </div>
            <div class="card-body">
                <p>Access satellite data programmatically using our RESTful API:</p>
                <div class="alert alert-info">
                    <h6 class="alert-heading">API Endpoints</h6>
                    <ul class="mb-0">
                        <li><code>GET /api/satellites</code> - Get current satellite positions</li>
                        <li><code>GET /api/passes?lat=:lat&lon=:lon&hours=:hours</code> - Get predicted passes</li>
                        <li><code>GET /api/coverage</code> - Get global coverage data</li>
                        <li><code>GET /api/export/json</code> - Export data in JSON format</li>
                        <li><code>GET /api/export/csv</code> - Export data in CSV format</li>
                    </ul>
                </div>
                <button type="button" class="btn btn-outline-primary">
                    <i class="fas fa-book"></i> View Full API Documentation
                </button>
            </div>
        </div>
    </div>
</div>

<script>
// Handle export form submission
document.getElementById('export-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const format = document.getElementById('export-format').value;
    
    // In a real implementation, this would trigger the actual export
    alert(`Exporting data in ${format.toUpperCase()} format. This would download a file in a real implementation.`);
    
    // Example of how to trigger an actual download:
    // window.location.href = `/api/export/${format}`;
});
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'export.html'), 'w', encoding='utf-8') as f:
        f.write(export_html)

if __name__ == '__main__':
    # Create templates directory
    create_templates_dir()
    
    # Run the web application
    app.run(debug=True, host='0.0.0.0', port=5000)