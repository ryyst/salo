import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

from utils.watcher import start_file_watcher
from utils.logging import Log
from config import execute_all_runners, set_cli_context
from utils.paths import (
    get_app_index_path,
    get_koje_static_path,
    resolve_app_file_path,
    get_content_type_from_path,
)
from utils.constants import KOJE_STATIC_FILES


class MultiAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, out_directory="_out", **kwargs):
        self.out_directory = out_directory
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # Parse the path to determine which app is being requested
        path_parts = self.path.lstrip("/").split("/")

        if not path_parts or not path_parts[0]:
            # Root path - serve koje app as main dashboard
            self.serve_koje_as_root()
            return

        app_name = path_parts[0]

        # Check if this is a static file request that should come from koje
        if app_name in KOJE_STATIC_FILES:
            if self.serve_static_from_koje(app_name):
                return

        # Build the relative path within the app
        relative_path = "/".join(path_parts[1:]) if len(path_parts) > 1 else ""
        file_path = resolve_app_file_path(app_name, relative_path, self.out_directory)

        if file_path:
            self.serve_file(file_path)
            return

        # File not found
        self.send_error(404, f"File not found: {self.path}")

    def serve_file(self, file_path: str):
        """Serve a file with appropriate content type and no-cache headers."""
        with open(file_path, "rb") as f:
            content = f.read()
            self.send_response(200)
            content_type = get_content_type_from_path(file_path)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            # Disable caching for dev server
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(content)

    def serve_app_listing(self):
        """Serve a simple HTML listing of available applications"""
        if not os.path.exists(self.out_directory):
            self.send_error(404, f"Output directory {self.out_directory} not found")
            return

        apps = [
            d
            for d in os.listdir(self.out_directory)
            if os.path.isdir(os.path.join(self.out_directory, d))
        ]

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Salo.fyi Development Server</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 10px 0; }}
        a {{ text-decoration: none; color: #0066cc; font-size: 18px; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Available Applications</h1>
    <ul>
"""
        for app in sorted(apps):
            html += f'        <li><a href="/{app}/">{app}</a></li>\n'

        html += """    </ul>
</body>
</html>"""

        content = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        # Disable caching for dev server
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(content)

    def serve_koje_as_root(self):
        """Serve the koje dashboard as the root index"""
        koje_path = get_app_index_path("koje", self.out_directory)

        if os.path.exists(koje_path):
            self.serve_file(koje_path)
        else:
            # Fallback to app listing if koje doesn't exist
            self.serve_app_listing()

    def serve_static_from_koje(self, filename):
        """Serve static files (icons, manifest, etc.) from koje directory"""
        static_path = get_koje_static_path(filename, self.out_directory)

        if os.path.exists(static_path):
            self.serve_file(static_path)
            return True
        return False


def host_dev_server(out_directory: str, port: int):
    """Host a multi-app development server serving all apps from _out directory."""
    from utils.constants import DEFAULT_CACHE_DIR, DEFAULT_DEV_HOST

    try:
        # Build all applications first
        Log.info("Building all applications...")

        set_cli_context(out_directory, DEFAULT_CACHE_DIR, ignore_cache=False)
        all_success = execute_all_runners()

        if not all_success:
            Log.error("Some applications failed to build initially")
        else:
            Log.info("All applications built successfully")

        observer = start_file_watcher(".")

        # Create a handler factory that passes the out_directory
        def handler_factory(*args, **kwargs):
            return MultiAppHandler(*args, out_directory=out_directory, **kwargs)

        server = HTTPServer((DEFAULT_DEV_HOST, port), handler_factory)
        Log.info(f"Serving all apps from {out_directory} at http://{DEFAULT_DEV_HOST}:{port}")
        Log.info("File watcher active - changes will trigger automatic rebuilds")
        server.serve_forever()

    except Exception as e:
        Log.exception("Failed to start the multi-app development server: %s", e, exc_info=e)

    except KeyboardInterrupt:
        Log.info("Shutting down file watcher...")
        try:
            observer.stop()
            observer.join()
        except:
            pass
        Log.info("Quitting, thanks for the ride!")
