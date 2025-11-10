#!/usr/bin/env python3
"""
Starlink Performance Monitor
Installation verification script.
"""

import sys
import importlib
import subprocess

def check_python_version():
    """Check if Python version meets requirements."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Required: Python 3.8+")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\nChecking dependencies...")
    
    # List of required packages
    required_packages = [
        'speedtest',
        'ping3',
        'pandas',
        'numpy',
        'matplotlib',
        'plotly',
        'dash',
        'sqlalchemy',
        'requests',
        'schedule',
        'telegram',
        'sklearn',
        'statsmodels',
        'openmeteo_requests',
        'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} - OK")
        except ImportError:
            # Try alternative names for some packages
            if package == 'speedtest':
                try:
                    importlib.import_module('speedtest_cli')
                    print(f"✓ speedtest_cli (as {package}) - OK")
                    continue
                except ImportError:
                    pass
            elif package == 'telegram':
                try:
                    importlib.import_module('telegram')
                    print(f"✓ python-telegram-bot (as {package}) - OK")
                    continue
                except ImportError:
                    pass
            elif package == 'sklearn':
                try:
                    importlib.import_module('sklearn')
                    print(f"✓ scikit-learn (as {package}) - OK")
                    continue
                except ImportError:
                    pass
            
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_database():
    """Check if database can be set up."""
    print("\nChecking database setup...")
    try:
        # Try to import the database models
        from monitor import Base, PerformanceMetric
        print("✓ Database models - OK")
        
        # Try to create database engine
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///test.db')
        Base.metadata.create_all(engine)
        print("✓ Database connection - OK")
        
        # Clean up test database
        import os
        if os.path.exists('test.db'):
            os.remove('test.db')
            
        return True
    except Exception as e:
        print(f"✗ Database setup - ERROR: {e}")
        return False

def main():
    """Main function to run all checks."""
    print("Starlink Performance Monitor - Installation Verification")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_database()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed! Installation is ready.")
        print("\nNext steps:")
        print("1. Copy config.example.json to config.json and update settings")
        print("2. Run 'python setup_database.py' to initialize the database")
        print("3. Run 'python monitor.py' to start monitoring")
        print("4. Run 'python web_app.py' to start the web interface")
    else:
        print("✗ Some checks failed. Please install missing dependencies.")
        print("\nTo install dependencies, run:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()