# Starlink Satellite Tracker Examples

This directory contains practical examples demonstrating how to use the Starlink Satellite Tracker application components.

## Examples Overview

### 1. Basic Tracking (`basic_tracking.py`)
Demonstrates core satellite tracking functionality:
- Initializing the tracker
- Updating TLE data
- Predicting satellite passes
- Clearing caches

**Run:**
```bash
python examples/basic_tracking.py
```

### 2. Data Processing (`data_processing.py`)
Shows data processing and export capabilities:
- Loading satellite data
- Analyzing constellation statistics
- Exporting to JSON and CSV formats
- Filtering data (example)

**Run:**
```bash
python examples/data_processing.py
```

### 3. Scheduling and Notifications (`scheduling_notifications.py`)
Illustrates automated scheduling and notification systems:
- Setting up scheduled tasks
- Configuring notification methods
- Testing email and Telegram notifications
- Manual task execution

**Run:**
```bash
python examples/scheduling_notifications.py
```

### 4. Web API Client (`web_api_client.py`)
Demonstrates how to interact with the web API:
- Making API requests to various endpoints
- Handling JSON responses
- Working with satellite data, passes, and coverage
- Cache management

**Run:**
```bash
# First start the web server in another terminal:
# python starlink_tracker.py web

# Then run the client example:
python examples/web_api_client.py
```

### 5. Complete Example (`complete_example.py`)
A comprehensive example combining all components:
- Core tracking functionality
- Data processing and export
- Scheduling setup
- Notification testing
- Resource cleanup

**Run:**
```bash
python examples/complete_example.py
```

## Running Examples

### Prerequisites
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For web API example, start the web server:
   ```bash
   python starlink_tracker.py web
   ```

### Execution
Run any example directly:
```bash
python examples/example_name.py
```

## Configuration

Examples use the main `config.json` file for configuration. Make sure it's properly set up before running examples.

### Notification Setup
To test notifications, configure email or Telegram in `config.json`:

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "recipient": "recipient@example.com"
    },
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token",
      "chat_id": "your_chat_id"
    }
  }
}
```

## Learning Path

1. **Start with `basic_tracking.py`** to understand core functionality
2. **Explore `data_processing.py`** to learn about data handling
3. **Try `scheduling_notifications.py`** to see automation features
4. **Test `web_api_client.py`** to understand API usage (requires web server)
5. **Run `complete_example.py`** to see everything working together

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running examples from the project root directory
2. **Network Issues**: Check internet connectivity for TLE data downloads
3. **Permission Errors**: Ensure write access to data directories
4. **Missing Dependencies**: Install all requirements from `requirements.txt`
5. **Configuration Errors**: Verify `config.json` is properly formatted

### Debugging

Enable debug logging by adding to examples:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Extending Examples

Feel free to modify these examples for your specific needs:
- Change observer locations
- Adjust prediction parameters
- Add custom data processing
- Implement additional notification methods
- Create specialized tracking workflows

## Contributing

If you create useful examples, consider contributing them back to the project:
1. Follow the coding standards in existing examples
2. Include clear documentation
3. Test your examples thoroughly
4. Submit a pull request