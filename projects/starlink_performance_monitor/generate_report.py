#!/usr/bin/env python3
"""
Starlink Performance Monitor
Report generation script.
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, Any

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from monitor import PerformanceMetric, Base

class ReportGenerator:
    """Generate performance reports in various formats."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the report generator with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db_engine = self._setup_database()
        self.db_session = sessionmaker(bind=self.db_engine)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _setup_database(self):
        """Setup database connection."""
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'postgresql':
            db_url = f"postgresql://{db_config.get('user', 'user')}:{db_config.get('password', 'password')}@" \
                     f"{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('name', 'starlink_monitor')}"
        else:
            db_url = "sqlite:///starlink_monitor.db"
            
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        return engine
        
    def get_metrics_for_period(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get performance metrics for a specific period.
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            DataFrame with metrics
        """
        session = self.db_session()
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
            
    def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
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
            'avg_download_mbps': df['download_mbps'].mean(),
            'avg_upload_mbps': df['upload_mbps'].mean(),
            'avg_ping_ms': df['ping_ms'].mean(),
            'max_download_mbps': df['download_mbps'].max(),
            'min_download_mbps': df['download_mbps'].min(),
            'max_upload_mbps': df['upload_mbps'].max(),
            'min_upload_mbps': df['upload_mbps'].min(),
            'max_ping_ms': df['ping_ms'].max(),
            'min_ping_ms': df['ping_ms'].min()
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
        
    def generate_weekly_report(self, date: datetime = None) -> Dict[str, Any]:
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
            'avg_download_mbps': df['download_mbps'].mean(),
            'avg_upload_mbps': df['upload_mbps'].mean(),
            'avg_ping_ms': df['ping_ms'].mean(),
            'max_download_mbps': df['download_mbps'].max(),
            'min_download_mbps': df['download_mbps'].min(),
            'max_upload_mbps': df['upload_mbps'].max(),
            'min_upload_mbps': df['upload_mbps'].min(),
            'max_ping_ms': df['ping_ms'].max(),
            'min_ping_ms': df['ping_ms'].min()
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
            'max_download_mbps': df['download_mbps'].max(),
            'min_download_mbps': df['download_mbps'].min(),
            'max_upload_mbps': df['upload_mbps'].max(),
            'min_upload_mbps': df['upload_mbps'].min(),
            'max_ping_ms': df['ping_ms'].max(),
            'min_ping_ms': df['ping_ms'].min()
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
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot download and upload speeds
        ax.plot(df['timestamp'], df['download_mbps'], label='Download Speed (Mbps)', color='blue')
        ax.plot(df['timestamp'], df['upload_mbps'], label='Upload Speed (Mbps)', color='green')
        
        # Plot ping on secondary y-axis
        ax2 = ax.twinx()
        ax2.plot(df['timestamp'], df['ping_ms'], label='Ping (ms)', color='red', alpha=0.7)
        
        # Formatting
        ax.set_xlabel('Time')
        ax.set_ylabel('Speed (Mbps)', color='black')
        ax2.set_ylabel('Ping (ms)', color='red')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add legends
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Title
        if 'date' in report_data:
            plt.title(f'Starlink Performance - {report_data["date"]}')
        elif 'week' in report_data:
            plt.title(f'Starlink Performance - {report_data["week"]}')
        else:
            plt.title('Starlink Performance')
            
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Performance chart saved as {filename}")

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
            report_date = None
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
        
    # Generate performance chart
    generator.generate_performance_chart(report_data, f"{output_base}_chart.png")

if __name__ == "__main__":
    main()