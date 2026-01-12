"""
Dashboard Web Server - Serves the dashboard over the network
Allows access to the dashboard from other computers on the same network.
"""

import os
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler to serve dashboard and related files"""

    def __init__(self, *args, base_dir=None, **kwargs):
        self.base_dir = base_dir or Path.cwd()
        super().__init__(*args, directory=str(base_dir), **kwargs)

    def log_message(self, format, *args):
        """Suppress default logging to reduce console noise"""
        pass  # Comment this out if you want to see access logs

    def end_headers(self):
        """Add headers to disable caching for real-time updates"""
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        """Handle GET requests"""
        # Redirect root to dashboard.html
        if self.path == '/':
            self.path = '/dashboard.html'

        # Serve the file
        return super().do_GET()


class DashboardServer:
    """Web server to host the dashboard on the network"""

    def __init__(self, config, base_dir):
        self.config = config
        self.base_dir = Path(base_dir)
        self.server = None
        self.server_thread = None
        self.running = False

    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            # Create a socket connection to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            # Connect to a public DNS server (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def start(self):
        """Start the web server"""
        if self.running:
            print("Dashboard server is already running")
            return False

        try:
            port = self.config.get('dashboard_port', 8080)

            # Create request handler with base directory
            def handler(*args, **kwargs):
                return DashboardRequestHandler(*args, base_dir=self.base_dir, **kwargs)

            # Start HTTP server on all interfaces (0.0.0.0)
            self.server = HTTPServer(('0.0.0.0', port), handler)
            self.running = True

            # Run server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()

            local_ip = self.get_local_ip()
            print(f"Dashboard server started!")
            print(f"  Local access: http://localhost:{port}")
            print(f"  Network access: http://{local_ip}:{port}")
            print(f"  Base directory: {self.base_dir}")

            return True
        except Exception as e:
            print(f"Failed to start dashboard server: {e}")
            self.running = False
            return False

    def _run_server(self):
        """Internal method to run the server"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False

    def stop(self):
        """Stop the web server"""
        if self.server and self.running:
            print("Stopping dashboard server...")
            self.running = False
            self.server.shutdown()
            self.server.server_close()
            if self.server_thread:
                self.server_thread.join(timeout=2)
            print("Dashboard server stopped")
            return True
        return False

    def get_access_url(self):
        """Get the URL to access the dashboard"""
        if not self.running:
            return None

        port = self.config.get('dashboard_port', 8080)
        local_ip = self.get_local_ip()
        return f"http://{local_ip}:{port}"

    def is_running(self):
        """Check if server is running"""
        return self.running


def test_server():
    """Test the server standalone"""
    from pathlib import Path

    # Mock config for testing
    class MockConfig:
        def get(self, key, default=None):
            return {'dashboard_port': 8080}.get(key, default)

    base_dir = Path(__file__).parent.parent
    config = MockConfig()
    server = DashboardServer(config, base_dir)

    print("Starting test server...")
    if server.start():
        print(f"Server running at: {server.get_access_url()}")
        print("Press Ctrl+C to stop")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")
            server.stop()
    else:
        print("Failed to start server")


if __name__ == "__main__":
    test_server()
