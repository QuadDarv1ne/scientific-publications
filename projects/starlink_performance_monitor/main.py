#!/usr/bin/env python3
"""
Starlink Performance Monitor
Main entry point for the application.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point."""
    print("Starlink Performance Monitor")
    print("=" * 30)
    print("Available commands:")
    print("  monitor     - Run the monitoring service")
    print("  web         - Start the web dashboard")
    print("  alerts      - Check for alerts")
    print("  report      - Generate reports")
    print("  setup-db    - Set up the database")
    print("  test        - Run tests")
    print("")
    print("Use 'python main.py <command>' to run a specific command")
    print("For help with a specific command, use 'python main.py <command> --help'")

if __name__ == "__main__":
    main()