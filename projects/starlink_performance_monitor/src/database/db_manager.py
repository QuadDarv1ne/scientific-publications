#!/usr/bin/env python3
"""
Starlink Performance Monitor
Database connection manager with connection pooling.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

# Add project root to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.models import Base
from src.utils.logging_config import get_logger


class DatabaseManager:
    """Database connection manager with connection pooling."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the database manager with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.engine = self._setup_engine()
        self.Session = sessionmaker(bind=self.engine)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def _setup_engine(self):
        """Setup database engine with connection pooling."""
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'postgresql':
            db_url = f"postgresql://{db_config.get('user', 'user')}:{db_config.get('password', 'password')}@" \
                     f"{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('name', 'starlink_monitor')}"
            
            # PostgreSQL connection pool configuration
            pool_config = {
                'poolclass': QueuePool,
                'pool_size': db_config.get('pool_size', 10),
                'max_overflow': db_config.get('max_overflow', 20),
                'pool_recycle': db_config.get('pool_recycle', 3600),
                'pool_pre_ping': db_config.get('pool_pre_ping', True),
                'echo': db_config.get('echo', False)
            }
        else:
            db_url = "sqlite:///starlink_monitor.db"
            
            # SQLite connection pool configuration
            pool_config = {
                'poolclass': StaticPool,
                'connect_args': {'check_same_thread': False},
                'echo': db_config.get('echo', False)
            }
            
        self.logger.info(f"Setting up database engine with pooling: {db_url}")
        
        # Create engine with connection pooling
        engine = create_engine(db_url, **pool_config)
        
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        
        return engine
        
    def get_session(self):
        """
        Get a database session from the pool.
        
        Returns:
            Database session
        """
        return self.Session()
        
    def close_engine(self):
        """Close the database engine and all connections."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database engine closed")
            
    def get_engine(self):
        """
        Get the database engine.
        
        Returns:
            Database engine
        """
        return self.engine


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None
_db_manager_lock = threading.Lock()


def get_database_manager(config_path: str = "config.json") -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        with _db_manager_lock:
            if _db_manager is None:
                _db_manager = DatabaseManager(config_path)
    return _db_manager


def get_db_session(config_path: str = "config.json"):
    """
    Get a database session from the global database manager.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Database session
    """
    db_manager = get_database_manager(config_path)
    return db_manager.get_session()


def close_database_manager():
    """Close the global database manager and its engine."""
    global _db_manager
    if _db_manager is not None:
        _db_manager.close_engine()
        _db_manager = None