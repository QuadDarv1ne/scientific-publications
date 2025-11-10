#!/usr/bin/env python3
"""
Starlink Performance Monitor
Report generation script.
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys
import os

# Add the src directory to the path so we can import from monitor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_manager import get_database_manager, get_db_session

from src.monitor.monitor import PerformanceMetric, Base
from src.utils.logging_config import setup_logging, get_logger# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

class ReportGenerator:
    """Generate performance reports in various formats."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the report generator with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db_manager = get_database_manager(config_path)
        self.db_engine = self.db_manager.get_engine()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _setup_database(self):
        """Setup database connection."""
        # This method is now handled by the database manager
        return self.db_manager.get_engine()
        
    def get_metrics_for_period(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get performance metrics for a specific period.
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            DataFrame with metrics
        """
        session = get_db_session()
        try:
            metrics = session.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.timestamp >= start_date,
                    PerformanceMetric.timestamp <= end_date
                )
            ).all()
            
            # Convert to DataFrame
            data = [{
                'timestamp': m.timestamp,
                'download_mbps': m.download_mbps,
                'upload_mbps': m.upload_mbps,
                'ping_ms': m.ping_ms,
                'packet_loss_percent': getattr(m, 'packet_loss_percent', 0),
                'server_name': m.server_name
            } for m in metrics]
            
            return pd.DataFrame(data)
        finally:
            session.close()
            
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a daily report.
        
        Args:
            date: Date for report (defaults to yesterday)
            
        Returns:
            Dictionary with report data
        """
        if date is None:
            date = datetime.utcnow() - timedelta(days=1)
            
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        df = self.get_metrics_for_period(start_date, end_date)
        
        if df.empty:
            return {
                'date': date.strftime('%Y-%m-%d'),
                'summary': 'No data available for this period',
                'metrics': {}
            }
            
        # Calculate summary statistics
        summary = {
            'total_tests': len(df),
            'avg_download_mbps': float(df['download_mbps'].mean()),
            'avg_upload_mbps': float(df['upload_mbps'].mean()),
            'avg_ping_ms': float(df['ping_ms'].mean()),
            'avg_packet_loss_percent': float(df['packet_loss_percent'].mean()),
            'max_download_mbps': float(df['download_mbps'].max()),
            'min_download_mbps': float(df['download_mbps'].min()),
            'max_upload_mbps': float(df['upload_mbps'].max()),
            'min_upload_mbps': float(df['upload_mbps'].min()),
            'max_ping_ms': float(df['ping_ms'].max()),
            'min_ping_ms': float(df['ping_ms'].min()),
            'max_packet_loss_percent': float(df['packet_loss_percent'].max()),
            'min_packet_loss_percent': float(df['packet_loss_percent'].min()),
            'std_download_mbps': float(df['download_mbps'].std()),
            'std_upload_mbps': float(df['upload_mbps'].std()),
            'std_ping_ms': float(df['ping_ms'].std()),
            'std_packet_loss_percent': float(df['packet_loss_percent'].std())
        }
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': summary,
            'metrics': df.to_dict(orient='records')
        }
        
    def generate_weekly_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a weekly report.
        
        Args:
            date: Date for report (defaults to last week)
            
        Returns:
            Dictionary with report data
        """
        if date is None:
            date = datetime.utcnow()
            
        # Get start of week (Monday)
        start_date = date - timedelta(days=date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        df = self.get_metrics_for_period(start_date, end_date)
        
        if df.empty:
            return {
                'week': f"Week {date.isocalendar()[1]}, {date.year}",
                'summary': 'No data available for this period',
                'metrics': {}
            }
            
        # Calculate summary statistics
        summary = {
            'total_tests': len(df),
            'avg_download_mbps': float(df['download_mbps'].mean()),
            'avg_upload_mbps': float(df['upload_mbps'].mean()),
            'avg_ping_ms': float(df['ping_ms'].mean()),
            'avg_packet_loss_percent': float(df['packet_loss_percent'].mean()),
            'max_download_mbps': float(df['download_mbps'].max()),
            'min_download_mbps': float(df['download_mbps'].min()),
            'max_upload_mbps': float(df['upload_mbps'].max()),
            'min_upload_mbps': float(df['upload_mbps'].min()),
            'max_ping_ms': float(df['ping_ms'].max()),
            'min_ping_ms': float(df['ping_ms'].min()),
            'max_packet_loss_percent': float(df['packet_loss_percent'].max()),
            'min_packet_loss_percent': float(df['packet_loss_percent'].min()),
            'std_download_mbps': float(df['download_mbps'].std()),
            'std_upload_mbps': float(df['upload_mbps'].std()),
            'std_ping_ms': float(df['ping_ms'].std()),
            'std_packet_loss_percent': float(df['packet_loss_percent'].std())
        }
        
        return {
            'week': f"Week {date.isocalendar()[1]}, {date.year}",
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': summary,
            'metrics': df.to_dict(orient='records')
        }
        
    def generate_custom_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate a custom report for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with report data
        """
        df = self.get_metrics_for_period(start_date, end_date)
        
        if df.empty:
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': 'No data available for this period',
                'metrics': {}
            }
            
        # Calculate summary statistics
        summary = {
            'total_tests': len(df),
            'avg_download_mbps': df['download_mbps'].mean(),
            'avg_upload_mbps': df['upload_mbps'].mean(),
            'avg_ping_ms': df['ping_ms'].mean(),
            'avg_packet_loss_percent': df['packet_loss_percent'].mean(),
            'max_download_mbps': df['download_mbps'].max(),
            'min_download_mbps': df['download_mbps'].min(),
            'max_upload_mbps': df['upload_mbps'].max(),
            'min_upload_mbps': df['upload_mbps'].min(),
            'max_ping_ms': df['ping_ms'].max(),
            'min_ping_ms': df['ping_ms'].min(),
            'max_packet_loss_percent': df['packet_loss_percent'].max(),
            'min_packet_loss_percent': df['packet_loss_percent'].min(),
            'std_download_mbps': df['download_mbps'].std(),
            'std_upload_mbps': df['upload_mbps'].std(),
            'std_ping_ms': df['ping_ms'].std(),
            'std_packet_loss_percent': df['packet_loss_percent'].std()
        }
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': summary,
            'metrics': df.to_dict(orient='records')
        }
        
    def save_report_as_json(self, report_data: Dict[str, Any], filename: str):
        """
        Save report data as JSON file.
        
        Args:
            report_data: Report data dictionary
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        print(f"Report saved as {filename}")
        
    def save_report_as_csv(self, report_data: Dict[str, Any], filename: str):
        """
        Save report metrics as CSV file.
        
        Args:
            report_data: Report data dictionary
            filename: Output filename
        """
        if 'metrics' in report_data and report_data['metrics']:
            df = pd.DataFrame(report_data['metrics'])
            df.to_csv(filename, index=False)
            print(f"Report saved as {filename}")
        else:
            print("No metrics data to save as CSV")
            
    def generate_performance_chart(self, report_data: Dict[str, Any], filename: str):
        """
        Generate a performance chart from report data.
        
        Args:
            report_data: Report data dictionary
            filename: Output filename for chart
        """
        if 'metrics' not in report_data or not report_data['metrics']:
            print("No metrics data to generate chart")
            return
            
        df = pd.DataFrame(report_data['metrics'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create a figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Starlink Performance Report', fontsize=16)
        
        # Plot 1: Download and Upload Speeds
        axes[0, 0].plot(df['timestamp'], df['download_mbps'], label='Download Speed (Mbps)', color='blue')
        axes[0, 0].plot(df['timestamp'], df['upload_mbps'], label='Upload Speed (Mbps)', color='green')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Speed (Mbps)')
        axes[0, 0].set_title('Download & Upload Speeds Over Time')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Format x-axis dates for the first plot
        axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        axes[0, 0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.setp(axes[0, 0].xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 2: Ping Performance
        axes[0, 1].plot(df['timestamp'], df['ping_ms'], label='Ping (ms)', color='red')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('Ping (ms)')
        axes[0, 1].set_title('Ping Performance Over Time')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Format x-axis dates for the second plot
        axes[0, 1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        axes[0, 1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.setp(axes[0, 1].xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 3: Packet Loss
        axes[1, 0].plot(df['timestamp'], df['packet_loss_percent'], label='Packet Loss (%)', color='orange')
        axes[1, 0].set_xlabel('Time')
        axes[1, 0].set_ylabel('Packet Loss (%)')
        axes[1, 0].set_title('Packet Loss Over Time')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Format x-axis dates for the third plot
        axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        axes[1, 0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 4: Distribution Histogram
        axes[1, 1].hist(df['download_mbps'], bins=20, alpha=0.7, label='Download Speed', color='blue')
        axes[1, 1].hist(df['upload_mbps'], bins=20, alpha=0.7, label='Upload Speed', color='green')
        axes[1, 1].set_xlabel('Speed (Mbps)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Speed Distribution')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Title based on report type
        if 'date' in report_data:
            fig.suptitle(f'Starlink Performance - {report_data["date"]}', fontsize=16)
        elif 'week' in report_data:
            fig.suptitle(f'Starlink Performance - {report_data["week"]}', fontsize=16)
        else:
            fig.suptitle('Starlink Performance', fontsize=16)
            
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Performance chart saved as {filename}")
        
    def generate_detailed_charts(self, report_data: Dict[str, Any], base_filename: str):
        """
        Generate detailed charts for the report.
        
        Args:
            report_data: Report data dictionary
            base_filename: Base filename for output files
        """
        if 'metrics' not in report_data or not report_data['metrics']:
            print("No metrics data to generate charts")
            return
            
        df = pd.DataFrame(report_data['metrics'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Generate time series chart
        self.generate_performance_chart(report_data, f"{base_filename}_timeseries.png")
        
        # Generate correlation heatmap
        self.generate_correlation_heatmap(report_data, f"{base_filename}_correlation.png")
        
        # Generate box plots
        self.generate_box_plots(report_data, f"{base_filename}_boxplot.png")
        
    def generate_correlation_heatmap(self, report_data: Dict[str, Any], filename: str):
        """
        Generate a correlation heatmap.
        
        Args:
            report_data: Report data dictionary
            filename: Output filename for chart
        """
        if 'metrics' not in report_data or not report_data['metrics']:
            print("No metrics data to generate correlation heatmap")
            return
            
        df = pd.DataFrame(report_data['metrics'])
        
        # Select numeric columns for correlation
        numeric_cols = ['download_mbps', 'upload_mbps', 'ping_ms', 'packet_loss_percent']
        corr_data = df[numeric_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(corr_data, cmap='coolwarm', interpolation='nearest')
        plt.colorbar()
        
        # Add labels
        plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
        plt.yticks(range(len(numeric_cols)), numeric_cols)
        
        # Add correlation values
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                plt.text(j, i, f'{corr_data.iloc[i, j]:.2f}', 
                        ha='center', va='center', fontsize=12)
        
        plt.title('Performance Metrics Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Correlation heatmap saved as {filename}")
        
    def generate_box_plots(self, report_data: Dict[str, Any], filename: str):
        """
        Generate box plots for performance metrics.
        
        Args:
            report_data: Report data dictionary
            filename: Output filename for chart
        """
        if 'metrics' not in report_data or not report_data['metrics']:
            print("No metrics data to generate box plots")
            return
            
        df = pd.DataFrame(report_data['metrics'])
        
        # Create box plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Performance Metrics Distribution', fontsize=16)
        
        # Download speed box plot
        axes[0, 0].boxplot(df['download_mbps'])
        axes[0, 0].set_title('Download Speed (Mbps)')
        axes[0, 0].set_ylabel('Mbps')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Upload speed box plot
        axes[0, 1].boxplot(df['upload_mbps'])
        axes[0, 1].set_title('Upload Speed (Mbps)')
        axes[0, 1].set_ylabel('Mbps')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Ping box plot
        axes[1, 0].boxplot(df['ping_ms'])
        axes[1, 0].set_title('Ping (ms)')
        axes[1, 0].set_ylabel('ms')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Packet loss box plot
        axes[1, 1].boxplot(df['packet_loss_percent'])
        axes[1, 1].set_title('Packet Loss (%)')
        axes[1, 1].set_ylabel('%')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Box plots saved as {filename}")

def main():
    """Main entry point for the report generation script."""
    parser = argparse.ArgumentParser(description='Generate Starlink Performance Reports')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--type', choices=['daily', 'weekly', 'custom'], default='daily',
                        help='Type of report to generate')
    parser.add_argument('--start', help='Start date for custom report (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date for custom report (YYYY-MM-DD)')
    parser.add_argument('--date', help='Date for daily report (YYYY-MM-DD, defaults to yesterday)')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output filename (without extension)')
    
    args = parser.parse_args()
    
    # Initialize report generator
    generator = ReportGenerator(args.config)
    
    # Generate report based on type
    if args.type == 'daily':
        if args.date:
            report_date = datetime.strptime(args.date, '%Y-%m-%d')
        else:
            report_date = datetime.utcnow() - timedelta(days=1)
        report_data = generator.generate_daily_report(report_date)
        default_output = f"daily_report_{report_data['date']}"
    elif args.type == 'weekly':
        report_data = generator.generate_weekly_report()
        default_output = f"weekly_report_{datetime.now().strftime('%Y-%m-%d')}"
    else:  # custom
        if not args.start or not args.end:
            parser.error("--start and --end required for custom reports")
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
        report_data = generator.generate_custom_report(start_date, end_date)
        default_output = f"custom_report_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}"
    
    # Determine output filename
    output_base = args.output if args.output else default_output
    
    # Save report in requested format
    if args.format in ['json', 'both']:
        generator.save_report_as_json(report_data, f"{output_base}.json")
        
    if args.format in ['csv', 'both']:
        generator.save_report_as_csv(report_data, f"{output_base}.csv")
        
    # Generate performance charts
    generator.generate_detailed_charts(report_data, output_base)

if __name__ == "__main__":
    main()