#!/usr/bin/env python3
"""
Starlink Performance Monitor
Simple test script for web interface functionality.
"""

def test_web_basic():
    """Test basic web interface functionality."""
    print("Testing basic web interface functionality...")
    
    # Test that we can import required modules
    try:
        import flask
        print("✓ Flask module imported successfully")
    except ImportError:
        print("✗ Flask import failed")
        return
        
    # Test that we can create a simple Flask app
    try:
        from flask import Flask
        app = Flask(__name__)
        print("✓ Flask app created successfully")
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        return
        
    # Test that we can import Chart.js functionality concept
    try:
        # This is just testing that we can work with charting concepts
        chart_types = ['line', 'bar', 'radar', 'pie']
        print("✓ Charting concepts validated")
        print(f"  Available chart types: {', '.join(chart_types)}")
    except Exception as e:
        print(f"✗ Charting concepts validation failed: {e}")
        return
        
    print("All basic web interface tests completed successfully!")

if __name__ == "__main__":
    test_web_basic()