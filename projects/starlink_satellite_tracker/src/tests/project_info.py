#!/usr/bin/env python3
"""
Project information utility for Starlink Satellite Tracker
Provides an overview of the project structure and capabilities
"""

from datetime import datetime


def show_project_structure():
    """Display the project directory structure."""
    print("=== Starlink Satellite Tracker Project Structure ===\n")

    # Define the project structure
    structure = {
        "Root Directory": [
            "README.md - Project documentation",
            "requirements.txt - Python dependencies",
            "config.json - Configuration file",
            "main.py - Core tracking functionality",
            "web_app.py - Web interface",
            "notify.py - Notification system",
            "data_processor.py - Data handling utilities",
            "test_tracker.py - Unit tests",
            "demo.py - Demonstration script",
        ],
        "Data Directory": ["data/ - Main data storage", "data/tle_cache/ - TLE data cache"],
        "Templates Directory": [
            "templates/ - Web interface templates",
            "templates/base.html - Base template",
            "templates/index.html - Main dashboard",
            "templates/passes.html - Pass predictions",
            "templates/coverage.html - Coverage map",
            "templates/settings.html - Configuration",
            "templates/export.html - Data export",
        ],
    }

    for section, items in structure.items():
        print(f"{section}:")
        for item in items:
            print(f"  ├── {item}")
        print()


def show_features():
    """Display the main features of the project."""
    print("=== Key Features ===\n")

    features = [
        "📡 Real-time satellite tracking with TLE data from Celestrak",
        "🌍 Precise satellite positioning using Skyfield library",
        "🗺️ Interactive 3D orbit visualization (matplotlib/plotly)",
        "📍 Pass prediction over user location",
        "🔔 Notifications via email or Telegram bot",
        "📊 Data export to CSV/JSON formats",
        "🌐 Global Starlink coverage mapping",
        "⚙️ Web dashboard with multiple views",
        "💾 Data caching for offline operation",
        "🔄 Automatic data updates",
        "📱 Responsive web interface",
    ]

    for feature in features:
        print(f"  {feature}")
    print()


def show_api_endpoints():
    """Display the available API endpoints."""
    print("=== Web API Endpoints ===\n")

    endpoints = {
        "GET /": "Main dashboard showing current satellite positions",
        "GET /passes": "Upcoming satellite passes calendar",
        "GET /coverage": "Global Starlink coverage map",
        "GET /settings": "Observer location and notification settings",
        "GET /export": "Data export interface",
        "GET /api/satellites": "Current satellite positions (JSON)",
        "GET /api/passes": "Predicted passes (JSON)",
        "GET /api/coverage": "Coverage data (JSON)",
        "GET /api/export/<format>": "Data export in various formats",
    }

    for endpoint, description in endpoints.items():
        print(f"  {endpoint:<25} - {description}")
    print()


def show_cli_options():
    """Display the command line options."""
    print("=== Command Line Options ===\n")

    options = [
        "--update        Force update TLE data",
        "--visualize     Show 3D visualization",
        "--notify        Send notifications for upcoming passes",
        "--debug         Enable debug logging",
    ]

    print("python main.py [options]")
    for option in options:
        print(f"  {option}")
    print()


def main():
    """Main function to display project information."""
    print("Starlink Satellite Tracker - Project Information")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    show_project_structure()
    show_features()
    show_api_endpoints()
    show_cli_options()

    print("For detailed usage, see README.md")
    print("\nTo start the web interface:")
    print("  python web_app.py")
    print("\nTo run the tracker:")
    print("  python main.py --help")


if __name__ == "__main__":
    main()
