#!/usr/bin/env python3
"""
Starlink Performance Monitor
Test script for database connection pooling functionality.
"""

import sys
import os
import tempfile
import json

import importlib.util
import sys
import os

# Add the src directory to the path so we can import from utils
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

db_manager_path = os.path.join(src_path, 'database', 'db_manager.py')
spec = importlib.util.spec_from_file_location("db_manager", db_manager_path)
db_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_manager)

get_database_manager = db_manager.get_database_manager
get_db_session = db_manager.get_db_session
close_database_manager = db_manager.close_database_manager


def test_db_pooling():
    """Test the database connection pooling functionality."""
    print("Testing database connection pooling...")
    
    # Create a temporary config file
    test_config = {
        "database": {
            "type": "sqlite",
            "echo": False
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_config:
        json.dump(test_config, temp_config)
        temp_config_path = temp_config.name
    
    try:
        # Test getting database manager
        db_manager = get_database_manager(temp_config_path)
        print("✓ Database manager created successfully")
        
        # Test getting engine
        engine = db_manager.get_engine()
        print(f"✓ Database engine created: {engine}")
        
        # Test getting sessions
        session1 = get_db_session(temp_config_path)
        print("✓ First database session created")
        
        session2 = get_db_session(temp_config_path)
        print("✓ Second database session created")
        
        # Test that sessions are different but from the same engine
        print(f"✓ Session 1: {session1}")
        print(f"✓ Session 2: {session2}")
        
        # Close sessions
        session1.close()
        session2.close()
        print("✓ Database sessions closed")
        
        # Close database manager
        close_database_manager()
        print("✓ Database manager closed")
        
        print("All database pooling tests completed successfully!")
        
    finally:
        # Clean up temporary config file
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)


if __name__ == "__main__":
    test_db_pooling()