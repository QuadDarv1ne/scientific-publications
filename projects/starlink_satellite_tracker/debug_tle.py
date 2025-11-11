import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our modules
from core.main import StarlinkTracker
from utils.config_manager import get_config

def main():
    print("Initializing Starlink Tracker...")
    config = get_config()
    print(f"Config loaded: {type(config)}")
    
    tracker = StarlinkTracker(config)
    print("Tracker initialized successfully")
    
    print("Attempting to download TLE data...")
    try:
        satellites = tracker.update_tle_data(force=True)
        print(f"Successfully loaded {len(satellites)} satellites")
        
        # Print first few satellites
        for i, sat in enumerate(satellites[:5]):
            print(f"  {i+1}. {sat.name}")
    except Exception as e:
        print(f"Error loading TLE data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()