# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data and reports
RUN mkdir -p /app/data /app/reports

# Create a non-root user
RUN useradd --create-home --shell /bin/bash starlink && \
    chown -R starlink:starlink /app
USER starlink

# Expose port
EXPOSE 8050

# Default command
CMD ["python", "monitor.py", "--config", "config.json"]