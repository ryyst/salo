import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

from utils.logging import Log


# Quick GPT muck for hosting files from urls without the .html suffix.
class SuffixlessHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/"):
            self.path += "index.html"

        elif not os.path.exists(self.path.lstrip("/")) and os.path.exists(
            self.path.lstrip("/") + ".html"
        ):
            self.path += ".html"

        return super().do_GET()


def host_dev_server(directory: str, port: int = 8000):
    """Host a static HTTP development server from any given directory."""
    try:
        os.chdir(directory)
        server = HTTPServer(("localhost", port), SuffixlessHandler)
        Log.info(f"Serving {directory} at http://localhost:{port}")
        server.serve_forever()

    except Exception as e:
        Log.exception("Failed to start the development server: %s", e, exc_info=e)

    except KeyboardInterrupt as e:
        Log.info("Quitting, thanks for the ride!")
