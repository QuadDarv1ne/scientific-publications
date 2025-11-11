#!/usr/bin/env python3
"""
Main entry point for Starlink Satellite Tracker
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point."""
    print("Starlink Satellite Tracker")
    print("=" * 30)
    print("Available commands:")
    print("  python starlink_tracker.py track     - Track satellites")
    print("  python starlink_tracker.py track --schedule - Start tracking with scheduler")
    print("  python starlink_tracker.py web       - Start web interface")
    print("  python starlink_tracker.py ar        - Start AR view (web interface)")
    print("  python starlink_tracker.py help      - Show this help")
    
    if len(sys.argv) < 2:
        return
    
    command = sys.argv[1]
    
    if command == "track":
        # Pass all arguments to the track command
        from core.main import main as track_main
        # Remove the first argument (script name) and 'track' command
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        track_main()
    elif command == "web":
        from web.web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    elif command == "ar":
        from web.web_app import app
        print("Starting AR view web interface...")
        print("Open your browser to http://localhost:5000/ar")
        app.run(debug=True, host='0.0.0.0', port=5000)
    elif command == "help":
        pass
    else:
        print(f"Unknown command: {command}")
        print("Use 'python starlink_tracker.py help' for available commands")

if __name__ == "__main__":
    main()