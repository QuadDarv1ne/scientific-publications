#!/usr/bin/env python3
"""
Starlink Performance Monitor
Database setup script.
"""

import json
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from monitor import Base, PerformanceMetric

def setup_database(config_path: str = "config.json"):
    """
    Set up the database based on configuration.
    
    Args:
        config_path: Path to configuration file
    """
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found, using SQLite defaults")
        config = {}
    
    # Get database configuration
    db_config = config.get('database', {})
    db_type = db_config.get('type', 'sqlite')
    
    # Create database engine
    if db_type == 'postgresql':
        db_url = f"postgresql://{db_config.get('user', 'user')}:{db_config.get('password', 'password')}@" \
                 f"{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('name', 'starlink_monitor')}"
    else:
        db_url = "sqlite:///starlink_monitor.db"
    
    print(f"Setting up database: {db_url}")
    
    # Create engine and initialize tables
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    print("Database setup completed successfully!")

def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(description='Set up Starlink Performance Monitor database')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    
    args = parser.parse_args()
    setup_database(args.config)

if __name__ == "__main__":
    main()