#!/usr/bin/env python3
"""
Starlink Performance Monitor
Database models for all entities.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from datetime import datetime, timedelta
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PerformanceMetric(Base):
    """ORM model for performance metrics storage."""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    server_name = Column(String(100), nullable=False)
    download_mbps = Column(Float)
    upload_mbps = Column(Float)
    ping_ms = Column(Float)
    packet_loss_percent = Column(Float)
    
    # Enhanced Starlink-specific metrics
    snr = Column(Float)  # Signal to noise ratio
    obstruction_fraction = Column(Float)  # Obstruction fraction
    downlink_throughput_mbps = Column(Float)  # Direct dish downlink throughput
    uplink_throughput_mbps = Column(Float)  # Direct dish uplink throughput
    location = Column(String(100), default='Starlink')  # Location identifier
    
    def __repr__(self):
        return f"<PerformanceMetric(server='{self.server_name}', timestamp='{self.timestamp}')>"


class WeatherData(Base):
    """ORM model for weather data storage."""
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature_2m = Column(Float)  # Temperature at 2 meters (°C)
    precipitation = Column(Float)   # Precipitation (mm)
    wind_speed_10m = Column(Float)  # Wind speed at 10 meters (km/h)
    cloud_cover = Column(Float)     # Cloud cover (%)
    pressure_msl = Column(Float)    # Pressure at mean sea level (hPa)
    humidity_2m = Column(Float)     # Relative humidity at 2 meters (%)
    # Add more fields as needed based on Open-Meteo parameters
    
    def __repr__(self):
        return f"<WeatherData(timestamp='{self.timestamp}', location=({self.latitude}, {self.longitude}))>"


class User(Base):
    """ORM model for application users (authentication & password reset)."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(30), default='user')
    # Use naive UTC datetimes consistently to avoid offset-aware vs. naive comparison issues
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    reset_token = Column(String(128), nullable=True, index=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    def set_reset_token(self, token: str, validity_minutes: int = 30):
        """Assign a password reset token with expiry (stored as naive UTC)."""
        self.reset_token = token
        self.reset_token_expiry = datetime.utcnow() + timedelta(minutes=validity_minutes)

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    def reset_token_valid(self) -> bool:
        if not self.reset_token or not self.reset_token_expiry:
            return False
        # Normalize to naive UTC for comparison to avoid mixing aware/naive datetimes
        now = datetime.utcnow()
        expiry = self.reset_token_expiry
        if getattr(expiry, 'tzinfo', None) is not None:
            try:
                expiry = expiry.replace(tzinfo=None)
            except Exception:
                pass
        return now <= expiry

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', role='{self.role}')>"