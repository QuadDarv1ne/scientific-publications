#!/usr/bin/env python3
"""
Starlink Satellite Tracker
Real-time satellite tracking and visualization system for SpaceX Starlink constellation
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta

# Import required libraries
try:
    import requests
    import numpy as np
    import pandas as pd
    from skyfield.api import load, EarthSatellite
    from skyfield.topos import wgs84
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


class StarlinkTracker:
    def __init__(self, config=None):
        """Initialize the Starlink tracker with optional configuration."""
        self.config = config or self._default_config()
        self.satellites = []
        self.ts = load.timescale()
        self.earth = load('earth.bsp')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.config['data_sources']['tle_cache_path'], exist_ok=True)
        
    def _default_config(self):
        """Return default configuration."""
        return {
            "data_sources": {
                "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
                "tle_cache_path": "data/tle_cache/",
                "max_cache_days": 7
            },
            "visualization": {
                "orbit_points": 100,
                "show_ground_track": True,
                "color_scheme": "dark"
            },
            "schedule": {
                "tle_update_cron": "0 0 */6 * *",
                "prediction_update_cron": "*/30 * * * *",
                "notification_check_cron": "*/15 * * * *"
            }
        }
    
    def update_tle_data(self, force=False):
        """Download latest TLE data from Celestrak."""
        cache_file = os.path.join(
            self.config['data_sources']['tle_cache_path'], 
            f"starlink_tle_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        
        # Check if we have recent cached data
        if not force and os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < timedelta(days=1):
                logging.info("Using cached TLE data")
                return self._load_tle_from_file(cache_file)
        
        # Download fresh data
        try:
            logging.info("Downloading latest TLE data from Celestrak")
            response = requests.get(self.config['data_sources']['celestrak_url'])
            response.raise_for_status()
            
            with open(cache_file, 'w') as f:
                f.write(response.text)
            
            return self._load_tle_from_file(cache_file)
        except Exception as e:
            logging.error(f"Failed to download TLE data: {e}")
            # Try to use cached data if available
            if os.path.exists(cache_file):
                logging.info("Using cached TLE data due to download failure")
                return self._load_tle_from_file(cache_file)
            else:
                raise
    
    def _load_tle_from_file(self, filename):
        """Load TLE data from file and create satellite objects."""
        self.satellites = []
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Process TLE data in groups of 3 lines
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                name = lines[i].strip()
                line1 = lines[i+1].strip()
                line2 = lines[i+2].strip()
                
                try:
                    satellite = EarthSatellite(line1, line2, name, self.ts)
                    self.satellites.append(satellite)
                except Exception as e:
                    logging.warning(f"Failed to load satellite {name}: {e}")
        
        logging.info(f"Loaded {len(self.satellites)} satellites")
        return self.satellites
    
    def predict_passes(self, latitude, longitude, altitude=0, 
                      hours_ahead=24, min_elevation=10):
        """Predict satellite passes over a location."""
        if not self.satellites:
            raise ValueError("No satellites loaded. Call update_tle_data() first.")
        
        # Set observer location
        observer = self.earth + wgs84.latlon(latitude, longitude, elevation_m=altitude)
        
        # Time range for predictions
        t0 = self.ts.now()
        t1 = self.ts.from_datetime(datetime.now() + timedelta(hours=hours_ahead))
        
        passes = []
        
        for satellite in self.satellites[:10]:  # Limit for performance
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
                        
                        passes.append({
                            'satellite': satellite.name,
                            'time': ti.utc_datetime(),
                            'altitude': alt.degrees,
                            'azimuth': az.degrees,
                            'distance': distance.km
                        })
            except Exception as e:
                logging.warning(f"Error predicting passes for {satellite.name}: {e}")
        
        return passes
    
    def visualize_orbits(self, hours=2):
        """Create 3D visualization of satellite orbits."""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            logging.error("Matplotlib not installed. Cannot create visualization.")
            return
        
        if not self.satellites:
            raise ValueError("No satellites loaded. Call update_tle_data() first.")
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Time range for orbit calculation
        t0 = self.ts.now()
        t1 = self.ts.from_datetime(datetime.now() + timedelta(hours=hours))
        times = self.ts.linspace(t0, t1, self.config['visualization']['orbit_points'])
        
        # Plot orbits for first 5 satellites
        for satellite in self.satellites[:5]:
            try:
                geocentric = satellite.at(times)
                x, y, z = geocentric.position.km
                
                ax.plot(x, y, z, label=satellite.name.split()[0])
            except Exception as e:
                logging.warning(f"Error plotting orbit for {satellite.name}: {e}")
        
        ax.set_xlabel('X (km)')
        ax.set_ylabel('Y (km)')
        ax.set_zlabel('Z (km)')
        ax.set_title('Starlink Satellite Orbits')
        ax.legend()
        
        plt.show()


def main():
    """Main entry point for the Starlink Tracker."""
    parser = argparse.ArgumentParser(description='Starlink Satellite Tracker')
    parser.add_argument('--update', action='store_true', 
                       help='Force update TLE data')
    parser.add_argument('--visualize', action='store_true', 
                       help='Show 3D visualization (default: False)')
    parser.add_argument('--notify', action='store_true', 
                       help='Send notifications for upcoming passes')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize tracker
    tracker = StarlinkTracker()
    
    try:
        # Update TLE data
        tracker.update_tle_data(force=args.update)
        
        # Show visualization if requested
        if args.visualize:
            tracker.visualize_orbits()
        
        # Example: Predict passes for a location (Moscow in this example)
        if args.notify or not any([args.visualize, args.update]):
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