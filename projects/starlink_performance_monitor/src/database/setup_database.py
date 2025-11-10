#!/usr/bin/env python3
"""
Starlink Performance Monitor
Database setup script.
"""

import json
import argparse
import logging
import sys
import os

# Add the src directory to the path so we can import from monitor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_manager import get_database_manager

from src.monitor.monitor import Base, PerformanceMetric
from src.utils.logging_config import setup_logging, get_logger
# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

def setup_database(config_path: str = "config.json"):
    """
    Set up the database based on configuration.
    
    Args:
        config_path: Path to configuration file
    """
    # Use the database manager to set up the database
    db_manager = get_database_manager(config_path)
    engine = db_manager.get_engine()
    
    logger.info(f"Database setup completed successfully with engine: {engine}")

def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(description='Set up Starlink Performance Monitor database')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    
    args = parser.parse_args()
    setup_database(args.config)

if __name__ == "__main__":
    main()