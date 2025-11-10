#!/usr/bin/env python3
"""
Starlink Performance Monitor
Main entry point for the application.
"""

import sys
import os
import argparse
import subprocess

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_monitor(args):
    """Run the monitoring service."""
    cmd = [sys.executable, 'src/monitor/monitor.py'] + args
    subprocess.run(cmd)

def run_web(args):
    """Start the web dashboard."""
    cmd = [sys.executable, 'src/web/web_app.py'] + args
    subprocess.run(cmd)

def run_alerts(args):
    """Check for alerts."""
    cmd = [sys.executable, 'src/alerts/alerts.py'] + args
    subprocess.run(cmd)

def run_reports(args):
    """Generate reports."""
    cmd = [sys.executable, 'src/reports/generate_report.py'] + args
    subprocess.run(cmd)

def setup_database(args):
    """Set up the database."""
    cmd = [sys.executable, 'src/database/setup_database.py'] + args
    subprocess.run(cmd)

def run_tests(args):
    """Run tests."""
    cmd = [sys.executable, '-m', 'pytest', 'tests/'] + args
    subprocess.run(cmd)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Run the monitoring service')
    monitor_parser.add_argument('monitor_args', nargs=argparse.REMAINDER, help='Arguments to pass to monitor.py')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start the web dashboard')
    web_parser.add_argument('web_args', nargs=argparse.REMAINDER, help='Arguments to pass to web_app.py')
    
    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='Check for alerts')
    alerts_parser.add_argument('alerts_args', nargs=argparse.REMAINDER, help='Arguments to pass to alerts.py')
    
    # Reports command
    reports_parser = subparsers.add_parser('report', help='Generate reports')
    reports_parser.add_argument('reports_args', nargs=argparse.REMAINDER, help='Arguments to pass to generate_report.py')
    
    # Database setup command
    db_parser = subparsers.add_parser('setup-db', help='Set up the database')
    db_parser.add_argument('db_args', nargs=argparse.REMAINDER, help='Arguments to pass to setup_database.py')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('test_args', nargs=argparse.REMAINDER, help='Arguments to pass to pytest')
    
    # Show help if no command is given
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == 'monitor':
        run_monitor(args.monitor_args)
    elif args.command == 'web':
        run_web(args.web_args)
    elif args.command == 'alerts':
        run_alerts(args.alerts_args)
    elif args.command == 'report':
        run_reports(args.reports_args)
    elif args.command == 'setup-db':
        setup_database(args.db_args)
    elif args.command == 'test':
        run_tests(args.test_args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()