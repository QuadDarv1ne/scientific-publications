#!/usr/bin/env python3
"""
Starlink Performance Monitor
Simple test script for database functionality.
"""

import sys
import os
import tempfile
import json

def test_db_basic():
    """Test basic database functionality."""
    print("Testing basic database functionality...")
    
    # Just test that we can import SQLAlchemy
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError:
        print("✗ SQLAlchemy import failed")
        return
        
    # Test that we can create an in-memory SQLite database
    try:
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:memory:')
        print("✓ In-memory SQLite database created")
        
        # Test that we can connect to it
        connection = engine.connect()
        print("✓ Database connection established")
        connection.close()
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return
        
    print("All basic database tests completed successfully!")

if __name__ == "__main__":
    test_db_basic()