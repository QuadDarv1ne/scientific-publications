#!/usr/bin/env python3
"""
Database migration script to add new Starlink-specific columns to the performance_metrics table.
"""

import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Float, text
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_manager import get_database_manager, get_db_session
from src.database.models import Base, PerformanceMetric

def migrate_database():
    """Add new Starlink-specific columns to the performance_metrics table."""
    print("Starting database migration...")
    
    try:
        # Get database manager
        db_manager = get_database_manager()
        engine = db_manager.get_engine()
        
        # Reflect the existing database schema
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Get the performance_metrics table
        if 'performance_metrics' in metadata.tables:
            performance_table = metadata.tables['performance_metrics']
            
            # Check if columns already exist
            existing_columns = [col.name for col in performance_table.columns]
            
            # Columns to add
            new_columns = [
                ('snr', 'FLOAT'),
                ('obstruction_fraction', 'FLOAT'),
                ('downlink_throughput_mbps', 'FLOAT'),
                ('uplink_throughput_mbps', 'FLOAT'),
                ('location', 'VARCHAR(100)')
            ]
            
            # Add new columns if they don't exist
            columns_added = []
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    # For SQLite, we need to use a different approach
                    if engine.dialect.name == 'sqlite':
                        # SQLite doesn't support adding columns directly to existing tables
                        # We need to create a new table and copy data
                        print(f"Adding column {col_name} to performance_metrics table...")
                        with engine.connect() as conn:
                            try:
                                conn.execute(text(f"ALTER TABLE performance_metrics ADD COLUMN {col_name} {col_type}"))
                                conn.commit()
                                columns_added.append(col_name)
                            except Exception as e:
                                print(f"Warning: Could not add column {col_name}: {e}")
                    else:
                        # For other databases, we can add columns directly
                        print(f"Adding column {col_name} to performance_metrics table...")
                        with engine.connect() as conn:
                            try:
                                conn.execute(text(f"ALTER TABLE performance_metrics ADD COLUMN {col_name} {col_type}"))
                                conn.commit()
                                columns_added.append(col_name)
                            except Exception as e:
                                print(f"Warning: Could not add column {col_name}: {e}")
            
            if columns_added:
                print(f"Successfully added columns: {', '.join(columns_added)}")
            else:
                print("All columns already exist or could not be added.")
        else:
            print("performance_metrics table not found. Creating tables...")
            Base.metadata.create_all(engine)
            print("Tables created successfully.")
            
        print("Database migration completed successfully.")
        
    except Exception as e:
        print(f"Error during database migration: {e}")
        return False
        
    return True

if __name__ == "__main__":
    migrate_database()