#!/usr/bin/env python3
"""
Starlink Satellite Tracker
Real-time satellite tracking and visualization system for SpaceX Starlink constellation
"""

import argparse
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import hashlib
import math


class StarlinkTrackerError(Exception):
    """Base exception class for Starlink Tracker errors."""
    pass


class TLEDataError(StarlinkTrackerError):
    """Exception raised for TLE data related errors."""
    pass


class PredictionError(StarlinkTrackerError):
    """Exception raised for prediction related errors."""
    pass


class SchedulerError(StarlinkTrackerError):
    """Exception raised for scheduler related errors."""
    pass


class VisualizationError(StarlinkTrackerError):
    """Exception raised for visualization related errors."""
    pass

# Import required libraries
try:
    import requests
    import numpy as np
    import pandas as pd
    from skyfield.api import load, EarthSatellite, Topos
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

# Import our configuration manager
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.config_manager import get_config


class TLECache:
    """Cache for TLE data with expiration and file-based persistence."""
    
    def __init__(self, max_age_hours: int = 24, cache_dir: str = "data/tle_cache/"):
        self.cache = {}
        self.timestamps = {}
        self.max_age = timedelta(hours=max_age_hours)
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_filename(self, url: str) -> str:
        """Generate a safe filename for cached TLE data."""
        # Create a hash of the URL for the filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"tle_cache_{url_hash}.txt")
    
    def get(self, url: str) -> Optional[str]:
        """Retrieve cached TLE data from memory or file if not expired."""
        # First check in-memory cache
        if url in self.cache:
            age = datetime.now() - self.timestamps[url]
            if age < self.max_age:
                self.logger.debug(f"TLE in-memory cache hit for {url}, age: {age}")
                return self.cache[url]
            else:
                self.logger.debug(f"TLE in-memory cache expired for {url}, age: {age}")
                del self.cache[url]
                del self.timestamps[url]
        
        # Check file-based cache
        cache_file = self._get_cache_filename(url)
        if os.path.exists(cache_file):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                age = datetime.now() - file_time
                if age < self.max_age:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = f.read()
                    # Store in memory cache for faster access next time
                    self.cache[url] = data
                    self.timestamps[url] = file_time
                    self.logger.debug(f"TLE file cache hit for {url}, age: {age}")
                    return data
                else:
                    self.logger.debug(f"TLE file cache expired for {url}, age: {age}")
                    os.remove(cache_file)  # Remove expired cache file
            except Exception as e:
                self.logger.warning(f"Error reading TLE cache file for {url}: {e}")
        
        return None
    
    def put(self, url: str, data: str) -> None:
        """Store TLE data in both memory and file cache."""
        # Store in memory cache
        self.cache[url] = data
        self.timestamps[url] = datetime.now()
        self.logger.debug(f"TLE data cached in memory for {url}")
        
        # Store in file cache
        try:
            cache_file = self._get_cache_filename(url)
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(data)
            self.logger.debug(f"TLE data cached in file for {url}")
        except Exception as e:
            self.logger.warning(f"Error writing TLE cache file for {url}: {e}")
    
    def clear(self) -> None:
        """Clear all cached TLE data from both memory and files."""
        # Clear memory cache
        self.cache.clear()
        self.timestamps.clear()
        self.logger.debug("TLE memory cache cleared")
        
        # Clear file cache
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.startswith("tle_cache_") and filename.endswith(".txt"):
                    os.remove(os.path.join(self.cache_dir, filename))
            self.logger.debug("TLE file cache cleared")
        except Exception as e:
            self.logger.warning(f"Error clearing TLE file cache: {e}")


class StarlinkTracker:
    def __init__(self, config=None):
        """Initialize the Starlink tracker with optional configuration."""
        self.config = config or get_config()
        self.satellites = []
        self.ts = load.timescale()  # Initialize time scale
        self.earth = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load Earth data
        try:
            self.earth = load('earth.bsp')
            self.logger.info("Earth data loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load earth.bsp: {e}")
            self.earth = None
        
        # Create data directory if it doesn't exist
        try:
            os.makedirs(self.config['data_sources']['tle_cache_path'], exist_ok=True)
            self.logger.info(f"Data directory ensured: {self.config['data_sources']['tle_cache_path']}")
        except Exception as e:
            self.logger.error(f"Failed to create data directory: {e}")
            raise
        
        # Initialize scheduler
        self.scheduler = None
        
        # Initialize TLE cache
        self.tle_cache = TLECache(max_age_hours=6, cache_dir=self.config['data_sources']['tle_cache_path'])
        
        # Cache for prediction results
        self.prediction_cache = {}
        self.prediction_cache_timestamps = {}
        self.prediction_cache_max_age = timedelta(minutes=15)
        
        # File-based cache for prediction results
        self.prediction_cache_dir = os.path.join(self.config['data_sources']['tle_cache_path'], 'predictions')
        os.makedirs(self.prediction_cache_dir, exist_ok=True)
    
    def _generate_prediction_cache_key(self, latitude: float, longitude: float, 
                                     hours_ahead: int, min_elevation: float) -> str:
        """Generate a cache key for prediction results."""
        key_data = f"{latitude}_{longitude}_{hours_ahead}_{min_elevation}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_prediction_cache_filename(self, cache_key: str) -> str:
        """Generate a filename for cached prediction results."""
        return os.path.join(self.prediction_cache_dir, f"prediction_{cache_key}.json")
    
    def _load_prediction_from_file(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Load prediction results from file cache."""
        cache_file = self._get_prediction_cache_filename(cache_key)
        if os.path.exists(cache_file):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                age = datetime.now() - file_time
                if age < self.prediction_cache_max_age:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    # Convert time strings back to datetime objects
                    for item in data:
                        item['time'] = datetime.fromisoformat(item['time'])
                    return data
                else:
                    os.remove(cache_file)  # Remove expired cache file
            except Exception as e:
                self.logger.warning(f"Error reading prediction cache file: {e}")
        return None
    
    def _save_prediction_to_file(self, cache_key: str, data: List[Dict[str, Any]]) -> None:
        """Save prediction results to file cache."""
        try:
            cache_file = self._get_prediction_cache_filename(cache_key)
            # Convert datetime objects to strings for JSON serialization
            serializable_data = []
            for item in data:
                item_copy = item.copy()
                item_copy['time'] = item_copy['time'].isoformat()
                serializable_data.append(item_copy)
            with open(cache_file, 'w') as f:
                json.dump(serializable_data, f)
        except Exception as e:
            self.logger.warning(f"Error writing prediction cache file: {e}")
    
    def update_tle_data(self, force=False) -> List[EarthSatellite]:
        """Download latest TLE data from Celestrak."""
        try:
            cache_file = os.path.join(
                self.config['data_sources']['tle_cache_path'], 
                f"starlink_tle_{datetime.now().strftime('%Y%m%d')}.txt"
            )
            
            # Check if we have recent cached data
            if not force and os.path.exists(cache_file):
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                    if datetime.now() - file_time < timedelta(days=1):
                        self.logger.info("Using cached TLE data")
                        return self._load_tle_from_file(cache_file)
                except Exception as e:
                    self.logger.warning(f"Error checking cache file timestamp: {e}")
            
            # Try primary source first
            urls_to_try = [self.config['data_sources']['celestrak_url']]
            
            # Add backup URLs if available
            if 'backup_urls' in self.config['data_sources']:
                urls_to_try.extend(self.config['data_sources']['backup_urls'])
            
            # Try each URL until one works
            for url in urls_to_try:
                try:
                    # Check TLE cache first
                    cached_tle = self.tle_cache.get(url)
                    if cached_tle and not force:
                        self.logger.info(f"Using cached TLE data from memory cache for {url}")
                        # Save to file
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            f.write(cached_tle)
                        return self._load_tle_from_file(cache_file)
                    
                    self.logger.info(f"Downloading latest TLE data from {url}")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    # Cache the TLE data
                    self.tle_cache.put(url, response.text)
                    
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    return self._load_tle_from_file(cache_file)
                except Exception as e:
                    self.logger.warning(f"Failed to download TLE data from {url}: {e}")
                    continue
            
            # If all sources failed, try to use cached data if available
            if os.path.exists(cache_file):
                self.logger.info("Using cached TLE data due to download failure")
                return self._load_tle_from_file(cache_file)
            else:
                raise Exception("Failed to download TLE data from all sources and no cached data available")
                
        except Exception as e:
            self.logger.error(f"Error updating TLE data: {e}")
            raise
    
    def _load_tle_from_file(self, filename) -> List[EarthSatellite]:
        """Load TLE data from file and create satellite objects."""
        try:
            self.satellites = []
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter out empty lines
            lines = [line.strip() for line in lines if line.strip()]
            
            # Process TLE data in groups of 3 lines
            loaded_count = 0
            error_count = 0
            
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    name = lines[i].strip()
                    line1 = lines[i+1].strip()
                    line2 = lines[i+2].strip()
                    
                    try:
                        satellite = EarthSatellite(line1, line2, name, self.ts)
                        self.satellites.append(satellite)
                        loaded_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to load satellite {name}: {e}")
                        error_count += 1
            
            self.logger.info(f"Loaded {loaded_count} satellites, {error_count} errors")
            return self.satellites
            
        except Exception as e:
            self.logger.error(f"Error loading TLE from file {filename}: {e}")
            raise
    
    def start_scheduler(self) -> bool:
        """Start the automated scheduler for background tasks."""
        try:
            # Import scheduler here to avoid circular imports
            from utils.scheduler import StarlinkScheduler
            
            self.scheduler = StarlinkScheduler(self.config, self)
            success = self.scheduler.start_scheduler()
            if success:
                self.logger.info("Scheduler started successfully")
            else:
                self.logger.warning("Failed to start scheduler")
            return success if success is not None else True
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            return False
    
    def stop_scheduler(self) -> bool:
        """Stop the automated scheduler."""
        try:
            if self.scheduler:
                success = self.scheduler.stop_scheduler()
                if success:
                    self.logger.info("Scheduler stopped successfully")
                else:
                    self.logger.warning("Failed to stop scheduler")
                return success if success is not None else True
            else:
                self.logger.warning("No scheduler to stop")
                return True
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
            return False
    
    def predict_passes(self, latitude: float, longitude: float, altitude: float = 0, 
                      hours_ahead: int = 24, min_elevation: float = 10) -> List[Dict[str, Any]]:
        """Predict satellite passes over a location."""
        try:
            # Generate cache key
            cache_key = self._generate_prediction_cache_key(latitude, longitude, hours_ahead, min_elevation)
            
            # Check if we have cached results in memory
            if cache_key in self.prediction_cache:
                cache_age = datetime.now() - self.prediction_cache_timestamps[cache_key]
                if cache_age < self.prediction_cache_max_age:
                    self.logger.info(f"Using in-memory cached prediction results, age: {cache_age}")
                    return self.prediction_cache[cache_key]
                else:
                    # Remove expired cache entry
                    del self.prediction_cache[cache_key]
                    del self.prediction_cache_timestamps[cache_key]
            
            # Check file-based cache
            file_cached_data = self._load_prediction_from_file(cache_key)
            if file_cached_data:
                self.logger.info(f"Using file-based cached prediction results")
                # Store in memory cache for faster access next time
                self.prediction_cache[cache_key] = file_cached_data
                self.prediction_cache_timestamps[cache_key] = datetime.now() - timedelta(minutes=5)  # Assume it's 5 minutes old
                return file_cached_data
            
            if not self.satellites:
                raise ValueError("No satellites loaded. Call update_tle_data() first.")
            
            if self.earth is None:
                raise ValueError("Earth data not loaded. Check internet connection.")
            
            if self.ts is None:
                raise ValueError("Time scale not initialized.")
            
            # Validate input parameters
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
            if hours_ahead <= 0:
                raise ValueError(f"Invalid hours_ahead: {hours_ahead}. Must be positive.")
            if min_elevation < 0:
                raise ValueError(f"Invalid min_elevation: {min_elevation}. Must be non-negative.")
            
            # Set observer location
            observer = self.earth + Topos(latitude, longitude, elevation_m=altitude)
            
            # Time range for predictions
            t0 = self.ts.now()
            t1 = self.ts.from_datetime(datetime.now() + timedelta(hours=hours_ahead))
            
            passes = []
            
            # Process all satellites for more comprehensive results
            for satellite in self.satellites:
                try:
                    # Find events (rise, culmination, set)
                    times, events = satellite.find_events(observer, t0, t1, 
                                                        altitude_degrees=min_elevation)
                    
                    for ti, event in zip(times, events):
                        if event == 0:  # Rise
                            # Get satellite position at rise time
                            difference = satellite - observer
                            topocentric = difference.at(ti)
                            alt, az, distance = topocentric.altaz()
                            
                            # Calculate additional information
                            velocity = self._calculate_velocity(satellite, ti, observer)
                            brightness = self._estimate_brightness(satellite, alt.degrees, distance.km)
                            
                            passes.append({
                                'satellite': satellite.name,
                                'time': ti.utc_datetime(),
                                'altitude': alt.degrees,
                                'azimuth': az.degrees,
                                'distance': distance.km,
                                'velocity': velocity,
                                'brightness': brightness
                            })
                except Exception as e:
                    self.logger.warning(f"Error predicting passes for {satellite.name}: {e}")
                    continue
            
            # Sort passes by time
            passes.sort(key=lambda x: x['time'])
            
            # Cache the results
            self.prediction_cache[cache_key] = passes
            self.prediction_cache_timestamps[cache_key] = datetime.now()
            
            # Save to file cache
            self._save_prediction_to_file(cache_key, passes)
            
            self.logger.info(f"Predicted {len(passes)} passes for {len(self.satellites)} satellites")
            return passes
            
        except Exception as e:
            self.logger.error(f"Error predicting passes: {e}")
            raise
    
    def _calculate_velocity(self, satellite: EarthSatellite, time, observer=None) -> float:
        """Calculate satellite velocity relative to observer or Earth center."""
        try:
            # Get positions at two nearby times
            t1 = time
            t2 = self.ts.from_datetime(time.utc_datetime() + timedelta(seconds=1))
            
            if observer is not None:
                # Calculate velocity relative to observer
                difference = satellite - observer
                pos1 = difference.at(t1)
                pos2 = difference.at(t2)
                
                # Calculate distance traveled in 1 second
                dist1 = pos1.distance().km
                dist2 = pos2.distance().km
                velocity = abs(dist2 - dist1)  # km/s
            else:
                # Calculate orbital velocity (relative to Earth center)
                geocentric1 = satellite.at(t1)
                geocentric2 = satellite.at(t2)
                
                # Get position vectors
                x1, y1, z1 = geocentric1.position.km
                x2, y2, z2 = geocentric2.position.km
                
                # Calculate distance traveled in 1 second
                dist1 = math.sqrt(x1**2 + y1**2 + z1**2)
                dist2 = math.sqrt(x2**2 + y2**2 + z2**2)
                velocity = abs(dist2 - dist1)  # km/s
                
                # For orbital velocity, we should calculate the magnitude of the velocity vector
                vx = (x2 - x1)  # km/s
                vy = (y2 - y1)  # km/s
                vz = (z2 - z1)  # km/s
                velocity = math.sqrt(vx**2 + vy**2 + vz**2)  # km/s
            
            return velocity
        except Exception as e:
            self.logger.warning(f"Error calculating velocity: {e}")
            return 0.0
    
    def _estimate_brightness(self, satellite: EarthSatellite, altitude: float, distance: float) -> float:
        """Estimate satellite brightness (magnitude)."""
        try:
            # Simplified brightness estimation model
            # This is a very rough approximation
            base_magnitude = 2.0  # Typical Starlink brightness
            
            # Adjust for altitude (higher = dimmer)
            altitude_factor = math.cos(math.radians(90 - altitude))
            
            # Adjust for distance (further = dimmer)
            distance_factor = (500 / distance) ** 2  # Assume 500km as reference
            
            # Combine factors
            brightness = base_magnitude - 2.5 * math.log10(altitude_factor * distance_factor)
            
            # Clamp to reasonable range
            return max(-2.0, min(10.0, brightness))
        except Exception as e:
            self.logger.warning(f"Error estimating brightness: {e}")
            return 5.0  # Default magnitude
    
    def get_satellite_info(self, satellite_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific satellite."""
        try:
            for satellite in self.satellites:
                if satellite.name == satellite_name:
                    # Get current position
                    t = self.ts.now()
                    geocentric = satellite.at(t)
                    subpoint = geocentric.subpoint()
                    
                    # Get orbital elements
                    elements = satellite.orbit_elements_at(t)
                    
                    # Calculate additional orbital parameters
                    velocity = self._calculate_velocity(satellite, t)  # Calculate orbital velocity
                    brightness = self._estimate_brightness(satellite, 45, subpoint.elevation.km)  # Estimate at 45° elevation
                    
                    return {
                        'name': satellite.name,
                        'norad_id': satellite.model.satnum,
                        'position': {
                            'latitude': subpoint.latitude.degrees,
                            'longitude': subpoint.longitude.degrees,
                            'altitude': subpoint.elevation.km
                        },
                        'orbit': {
                            'inclination': elements.inclination.degrees,
                            'eccentricity': elements.eccentricity,
                            'period': elements.period_in_days * 24 * 60,  # minutes
                            'semi_major_axis': elements.semi_major_axis.km,
                            'right_ascension': elements.longitude_of_ascending_node.degrees,
                            'argument_of_perigee': elements.argument_of_perigee.degrees,
                            'mean_anomaly': elements.mean_anomaly.degrees,
                            'mean_motion': elements.mean_motion.radians_per_day * 180 / math.pi / 86400  # rev/s
                        },
                        'characteristics': {
                            'velocity': velocity,  # km/s
                            'brightness': brightness,  # magnitude
                            'radar_cross_section': 'N/A'  # Would require additional data
                        },
                        'updated': t.utc_datetime().isoformat()
                    }
            return None
        except Exception as e:
            self.logger.error(f"Error getting satellite info for {satellite_name}: {e}")
            return None
    
    def visualize_orbits(self, hours: float = 2):
        """Create 3D visualization of satellite orbits."""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            self.logger.error("Matplotlib not installed. Cannot create visualization.")
            raise ImportError("Matplotlib not installed. Cannot create visualization.")
        
        try:
            if not self.satellites:
                raise ValueError("No satellites loaded. Call update_tle_data() first.")
            
            if self.ts is None:
                raise ValueError("Time scale not initialized.")
            
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Time range for orbit calculation
            t0 = self.ts.now()
            t1 = self.ts.from_datetime(datetime.now() + timedelta(hours=hours))
            times = self.ts.linspace(t0, t1, self.config['visualization']['orbit_points'])
            
            # Plot orbits for first 10 satellites
            satellites_to_plot = self.satellites[:10]
            
            for satellite in satellites_to_plot:
                try:
                    geocentric = satellite.at(times)
                    x, y, z = geocentric.position.km
                    
                    ax.plot(x, y, z, label=satellite.name.split()[0])
                except Exception as e:
                    self.logger.warning(f"Error plotting orbit for {satellite.name}: {e}")
                    continue
            
            ax.set_xlabel('X (km)')
            ax.set_ylabel('Y (km)')
            ax.set_zlabel('Z (km)')
            ax.set_title('Starlink Satellite Orbits')
            ax.legend()
            
            self.logger.info(f"Visualized orbits for {len(satellites_to_plot)} satellites")
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error visualizing orbits: {e}")
            raise
    
    def clear_caches(self) -> None:
        """Clear all caches."""
        self.tle_cache.clear()
        self.prediction_cache.clear()
        self.prediction_cache_timestamps.clear()
        # Clear prediction file cache
        try:
            for filename in os.listdir(self.prediction_cache_dir):
                if filename.startswith("prediction_") and filename.endswith(".json"):
                    os.remove(os.path.join(self.prediction_cache_dir, filename))
            self.logger.info("Prediction file cache cleared")
        except Exception as e:
            self.logger.warning(f"Error clearing prediction file cache: {e}")
        self.logger.info("All caches cleared")


def main():
    """Main entry point for the Starlink Tracker."""
    parser = argparse.ArgumentParser(description='Starlink Satellite Tracker')
    parser.add_argument('--update', action='store_true', 
                       help='Force update TLE data')
    parser.add_argument('--visualize', action='store_true', 
                       help='Show 3D visualization (default: False)')
    parser.add_argument('--notify', action='store_true', 
                       help='Send notifications for upcoming passes')
    parser.add_argument('--schedule', action='store_true', 
                       help='Start scheduler for automated tasks')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Initialize tracker
        tracker = StarlinkTracker()
        logger = logging.getLogger(__name__)
        logger.info("Starlink Tracker initialized successfully")
        
        # Update TLE data
        tracker.update_tle_data(force=args.update)
        
        # Show visualization if requested
        if args.visualize:
            tracker.visualize_orbits()
        
        # Start scheduler if requested
        if args.schedule:
            if tracker.start_scheduler():
                print("Scheduler started. Press Ctrl+C to stop.")
                try:
                    # Keep running
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping scheduler...")
                    tracker.stop_scheduler()
            else:
                print("Failed to start scheduler")
                sys.exit(1)
        
        # Example: Predict passes for a location (Moscow in this example)
        if args.notify or not any([args.visualize, args.update, args.schedule]):
            passes = tracker.predict_passes(latitude=55.7558, longitude=37.6173)
            print(f"Found {len(passes)} upcoming passes:")
            for p in passes[:10]:  # Show first 10
                print(f"  {p['satellite']}: {p['time'].strftime('%Y-%m-%d %H:%M:%S')} "
                      f"at {p['altitude']:.1f}° alt, {p['azimuth']:.1f}° az")
    
    except Exception as e:
        logging.error(f"Error running Starlink Tracker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()