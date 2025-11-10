#!/usr/bin/env python3
"""
Starlink Performance Monitor
Test script for logging functionality.
"""

import sys
import os
import tempfile
import logging

# Add the src directory to the path so we can import from utils
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
utils_path = os.path.join(src_path, 'utils')
sys.path.insert(0, src_path)
sys.path.insert(0, utils_path)

# Import the logging_config module
from logging_config import setup_logging, get_logger


def test_logging_setup():
    """Test the logging setup functionality."""
    print("Testing logging setup...")
    
    # Test basic setup
    logger = setup_logging()
    test_logger = get_logger(__name__)
    
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    
    print("Basic logging test completed.")
    
    # Test file logging
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")
        logger = setup_logging(log_file=log_file)
        test_logger = get_logger(__name__)
        
        test_logger.info("This is an info message to file")
        test_logger.warning("This is a warning message to file")
        test_logger.error("This is an error message to file")
        
        # Check if log file was created
        if os.path.exists(log_file):
            print("File logging test completed.")
            with open(log_file, 'r') as f:
                content = f.read()
                print(f"Log file content ({len(content)} characters):")
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print("ERROR: Log file was not created.")
    
    print("All logging tests completed.")


if __name__ == "__main__":
    test_logging_setup()