#!/usr/bin/env python3
"""
Starlink Performance Monitor
Database models for all entities.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

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