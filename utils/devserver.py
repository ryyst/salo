import os
from config import list_runners, execute_runner
from http.server import SimpleHTTPRequestHandler, HTTPServer

from utils.watcher import start_file_watcher
from utils.logging import Log


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
        static_files = [
            "manifest.json",
            "icon-192.png",
            "icon-512.png",
            "sw.js",
            "CNAME",
        ]
        if app_name in static_files:
            if self.serve_static_from_koje(app_name):
                return

        app_dir = os.path.join(self.out_directory, app_name)

        if os.path.isdir(app_dir):
            # Build the relative path within the app
            if len(path_parts) == 1 or (len(path_parts) == 2 and not path_parts[1]):
                # Just /appname or /appname/, serve index.html
                file_path = os.path.join(app_dir, "index.html")
            else:
                # /appname/file.html or /appname/subpath
                relative_path = "/".join(path_parts[1:])
                if relative_path.endswith("/"):
                    relative_path += "index.html"
                elif (
                    not relative_path.endswith(".html")
                    and not os.path.exists(os.path.join(app_dir, relative_path))
                    and os.path.exists(os.path.join(app_dir, relative_path + ".html"))
                ):
                    relative_path += ".html"
                file_path = os.path.join(app_dir, relative_path)

            if os.path.exists(file_path):
                # Serve the file from the app directory
                with open(file_path, "rb") as f:
                    content = f.read()
                    self.send_response(200)
                    if file_path.endswith(".html"):
                        self.send_header("Content-Type", "text/html")
                    elif file_path.endswith(".css"):
                        self.send_header("Content-Type", "text/css")
                    elif file_path.endswith(".js"):
                        self.send_header("Content-Type", "application/javascript")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                return

        # File not found
        self.send_error(404, f"File not found: {self.path}")

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
        self.end_headers()
        self.wfile.write(content)

    def serve_koje_as_root(self):
        """Serve the koje dashboard as the root index"""
        koje_path = os.path.join(self.out_directory, "koje", "index.html")

        if os.path.exists(koje_path):
            with open(koje_path, "rb") as f:
                content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        else:
            # Fallback to app listing if koje doesn't exist
            self.serve_app_listing()

    def serve_static_from_koje(self, filename):
        """Serve static files (icons, manifest, etc.) from koje directory"""
        static_path = os.path.join(self.out_directory, "koje", filename)

        if os.path.exists(static_path):
            with open(static_path, "rb") as f:
                content = f.read()
                self.send_response(200)

                # Set appropriate content type
                if filename.endswith(".json"):
                    self.send_header("Content-Type", "application/json")
                elif filename.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif filename.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript")
                else:
                    self.send_header("Content-Type", "application/octet-stream")

                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return True
        return False


def host_dev_server(out_directory: str = "_out", port: int = 8000):
    """Host a multi-app development server serving all apps from _out directory."""
    try:
        # Build all applications first
        Log.info("Building all applications...")

        all_success = True
        runners = list_runners()

        for runner_name in runners.keys():
            default_config = f"_confs/{runner_name}.json"

            if not os.path.exists(default_config):
                Log.warning(
                    f"Skipping runner '{runner_name}': config file not found at {default_config}"
                )
                continue

            success = execute_runner(
                runner_name,
                default_config,
                out_directory,
                "_cache",
                False,  # don't ignore cache
            )

            if not success:
                all_success = False
                Log.error(f"Initial build failed for runner '{runner_name}'")

        if not all_success:
            Log.error("Some applications failed to build initially")
        else:
            Log.info("All applications built successfully")

        observer = start_file_watcher(".")

        # Create a handler factory that passes the out_directory
        def handler_factory(*args, **kwargs):
            return MultiAppHandler(*args, out_directory=out_directory, **kwargs)

        server = HTTPServer(("localhost", port), handler_factory)
        Log.info(f"Serving all apps from {out_directory} at http://localhost:{port}")
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
