#!/usr/bin/env python3
"""
Web API Client Example

This example demonstrates how to interact with the Starlink Tracker web API
from a Python client application.
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the src directory to the path for local imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def get_api_data(base_url, endpoint, params=None):
    """
    Helper function to make API requests.
    
    Args:
        base_url (str): Base URL of the API
        endpoint (str): API endpoint
        params (dict, optional): Query parameters
        
    Returns:
        dict: JSON response data or None if error
    """
    try:
        url = f"{base_url}{endpoint}"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return None


def main():
    """Demonstrate web API client functionality."""
    
    print("🌐 Starlink Satellite Tracker - Web API Client Example")
    print("=" * 55)
    
    # Configuration
    BASE_URL = "http://localhost:5000"  # Default Flask development server
    TIMEOUT = 30
    
    try:
        # Test API connectivity
        print("🔍 Testing API connectivity...")
        try:
            response = requests.get(f"{BASE_URL}/api/satellites", timeout=TIMEOUT)
            if response.status_code == 200:
                print("✓ API is accessible")
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API at {BASE_URL}")
            print(f"   Make sure the web application is running:")
            print(f"   python starlink_tracker.py web")
            return
        
        # Get satellite data
        print("\n📡 Getting satellite data...")
        satellites_data = get_api_data(BASE_URL, "/api/satellites")
        
        if satellites_data:
            count = satellites_data.get('count', 0)
            print(f"✓ Retrieved data for {count} satellites")
            
            # Show first few satellites
            satellites = satellites_data.get('satellites', [])
            if satellites:
                print("   First 5 satellites:")
                for sat in satellites[:5]:
                    print(f"     - {sat.get('name', 'Unknown')}")
        else:
            print("❌ Failed to retrieve satellite data")
        
        # Get passes for a location
        print("\n📅 Getting satellite passes...")
        params = {
            'lat': 40.7128,  # New York City
            'lon': -74.0060,
            'hours': 48
        }
        
        passes_data = get_api_data(BASE_URL, "/api/passes", params)
        
        if passes_data:
            count = passes_data.get('count', 0)
            location = passes_data.get('location', {})
            lat = location.get('latitude', 'Unknown')
            lon = location.get('longitude', 'Unknown')
            
            print(f"✓ Found {count} passes for location ({lat}, {lon})")
            
            # Show first few passes
            passes = passes_data.get('passes', [])
            if passes:
                print("   Next 3 passes:")
                for p in passes[:3]:
                    time_str = p.get('time', 'Unknown')
                    satellite = p.get('satellite', 'Unknown')
                    altitude = p.get('altitude', 0)
                    print(f"     {satellite} at {time_str} (Alt: {altitude}°)")
        else:
            print("❌ Failed to retrieve pass data")
        
        # Get coverage data
        print("\n🌍 Getting coverage data...")
        coverage_data = get_api_data(BASE_URL, "/api/coverage")
        
        if coverage_data:
            total_satellites = coverage_data.get('total_satellites', 0)
            global_coverage = coverage_data.get('global_coverage', 0)
            print(f"✓ Global constellation data:")
            print(f"   Total satellites: {total_satellites}")
            print(f"   Global coverage: {global_coverage:.1f}%")
            
            # Show regional coverage
            regions = coverage_data.get('regions', [])
            if regions:
                print("   Regional coverage:")
                for region in regions:
                    name = region.get('name', 'Unknown')
                    coverage = region.get('coverage_percentage', 0)
                    print(f"     {name}: {coverage:.1f}%")
        else:
            print("❌ Failed to retrieve coverage data")
        
        # Test cache clearing
        print("\n🧹 Clearing API cache...")
        try:
            response = requests.post(f"{BASE_URL}/api/cache/clear", timeout=TIMEOUT)
            if response.status_code == 200:
                print("✓ API cache cleared successfully")
            else:
                print(f"❌ Cache clear failed with status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Cache clear request failed: {e}")
        
        print(f"\n✅ Web API client example completed successfully!")
        print(f"   For full functionality, ensure the web server is running:")
        print(f"   python starlink_tracker.py web")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()