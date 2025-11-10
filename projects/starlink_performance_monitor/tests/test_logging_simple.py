#!/usr/bin/env python3
"""
Starlink Performance Monitor
Simple test script for logging functionality.
"""

import logging
import os

def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging...")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("Basic logging test completed.")

if __name__ == "__main__":
    test_basic_logging()