import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.main import StarlinkTracker

def main():
    print("Initializing Starlink Tracker...")
    tracker = StarlinkTracker()
    print("Downloading TLE data...")
    satellites = tracker.update_tle_data()
    print(f"Loaded {len(satellites)} satellites")

if __name__ == "__main__":
    main()