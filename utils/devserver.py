import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

from utils.logging import Log


class MultiAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, out_directory="_out", **kwargs):
        self.out_directory = out_directory
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # Parse the path to determine which app is being requested
        path_parts = self.path.lstrip("/").split("/")

        if not path_parts or not path_parts[0]:
            # Root path - serve a directory listing of available apps
            self.serve_app_listing()
            return

        app_name = path_parts[0]
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


def host_dev_server(out_directory: str = "_out", port: int = 8000):
    """Host a multi-app development server serving all apps from _out directory."""
    try:
        # Create a handler factory that passes the out_directory
        def handler_factory(*args, **kwargs):
            return MultiAppHandler(*args, out_directory=out_directory, **kwargs)

        server = HTTPServer(("localhost", port), handler_factory)
        Log.info(f"Serving all apps from {out_directory} at http://localhost:{port}")
        server.serve_forever()

    except Exception as e:
        Log.exception(
            "Failed to start the multi-app development server: %s", e, exc_info=e
        )

    except KeyboardInterrupt:
        Log.info("Quitting, thanks for the ride!")
