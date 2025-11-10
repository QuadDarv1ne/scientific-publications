#!/usr/bin/env python3
"""
Starlink Performance Monitor
Main application entry point with CLI interface.
"""

import argparse
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.monitor.monitor import main as monitor_main
from src.web.web_app import main as web_main
from src.reports.generate_report import main as report_main
from src.ml.ml_analyzer import main as ml_main
from src.alerts.alerts import main as alerts_main
from src.database.setup_database import main as db_setup_main
from src.starlink.enhanced_monitor import main as enhanced_monitor_main

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor')
    parser.add_argument('command', choices=['monitor', 'web', 'report', 'ml', 'alerts', 'db-setup', 'enhanced-monitor'], 
                       help='Command to run')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    
    # Parse known args to get the command first
    args, remaining = parser.parse_known_args()
    
    # Now handle the specific command with its arguments
    if args.command == 'monitor':
        # Pass remaining arguments to monitor
        sys.argv = [sys.argv[0]] + remaining
        return monitor_main()
    elif args.command == 'enhanced-monitor':
        # Pass remaining arguments to enhanced monitor
        sys.argv = [sys.argv[0]] + remaining
        return enhanced_monitor_main()
    elif args.command == 'web':
        # Pass remaining arguments to web app
        sys.argv = [sys.argv[0]] + remaining
        return web_main()
    elif args.command == 'report':
        # Pass remaining arguments to report generator
        sys.argv = [sys.argv[0]] + remaining
        return report_main()
    elif args.command == 'ml':
        # Pass remaining arguments to ML analyzer
        sys.argv = [sys.argv[0]] + remaining
        return ml_main()
    elif args.command == 'alerts':
        # Pass remaining arguments to alerts system
        sys.argv = [sys.argv[0]] + remaining
        return alerts_main()
    elif args.command == 'db-setup':
        # Pass remaining arguments to database setup
        sys.argv = [sys.argv[0]] + remaining
        return db_setup_main()
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    exit(main())