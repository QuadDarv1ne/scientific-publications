#!/usr/bin/env python3
"""
Starlink Performance Monitor
Wrapper script for the report generation module.
"""

if __name__ == "__main__":
    # Import and run the main function from the src module
    from src.reports.generate_report import main
    main()