#!/usr/bin/env python3
"""
Starlink Performance Monitor
Manual testing script for running individual tests.
"""

import argparse
import json
from datetime import datetime
import sys
import os

# Add the src directory to the path so we can import from monitor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.monitor.monitor import StarlinkMonitor

def run_manual_test(config_path: str = "config.json", test_type: str = "all"):
    """
    Run manual tests based on type.
    
    Args:
        config_path: Path to configuration file
        test_type: Type of test to run (all, speed, ping)
    """
    print(f"Running manual test: {test_type}")
    print(f"Using configuration: {config_path}")
    print("-" * 50)
    
    # Initialize monitor
    monitor = StarlinkMonitor(config_path)
    
    if test_type == "speed" or test_type == "all":
        print("Running speed test...")
        results = monitor.run_speedtest()
        print(f"Download: {results['download_mbps']:.2f} Mbps")
        print(f"Upload: {results['upload_mbps']:.2f} Mbps")
        print(f"Ping: {results['ping_ms']:.2f} ms")
        print(f"Server: {results['server_name']}")
        print()
    
    if test_type == "ping" or test_type == "all":
        print("Running ping tests...")
        # Get ping servers from config
        config = monitor._load_config(config_path)
        ping_servers = config.get('monitoring', {}).get('starlink', {}).get('servers', [
            {'host': '8.8.8.8', 'name': 'Google DNS'},
            {'host': '1.1.1.1', 'name': 'Cloudflare'}
        ])
        
        for server in ping_servers:
            host = server['host']
            name = server['name']
            print(f"Ping test to {name} ({host}):")
            results = monitor.run_ping_test(host, count=5)
            print(f"  Average ping: {results['avg_ping_ms']:.2f} ms")
            print(f"  Packet loss: {results['packet_loss_percent']:.2f}%")
            print(f"  Min ping: {results['min_ping_ms']:.2f} ms")
            print(f"  Max ping: {results['max_ping_ms']:.2f} ms")
            print()

def main():
    """Main entry point for the manual test script."""
    parser = argparse.ArgumentParser(description='Manual test for Starlink Performance Monitor')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--type', default='all', choices=['all', 'speed', 'ping'], 
                        help='Type of test to run')
    
    args = parser.parse_args()
    run_manual_test(args.config, args.type)

if __name__ == "__main__":
    main()