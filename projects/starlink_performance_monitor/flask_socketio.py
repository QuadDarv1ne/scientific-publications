"""
Stub module for flask_socketio to prevent eventlet import errors on Python 3.14+
This is a minimal implementation for testing purposes only.
"""


class SocketIO:
    """Minimal SocketIO stub for testing"""
    
    def __init__(self, app=None, **kwargs):
        self.app = app
        
    def on(self, event, namespace=None):
        """Decorator stub"""
        def decorator(f):
            return f
        return decorator
    
    def emit(self, event, data, **kwargs):
        """Emit stub"""
        pass
    
    def run(self, app, **kwargs):
        """Run stub"""
        pass
