import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils.logging import Log

jinja = Environment(loader=FileSystemLoader([".", "templates"]), autoescape=select_autoescape())


#
# Simple general-purpose renderers for the most basic formats.
#


def render_html(data, template_path: str, auto_refresh_minutes=None):
    template = jinja.get_template(template_path)
    return template.render(data=data, auto_refresh_minutes=auto_refresh_minutes)


def render_stdout(data, params=None):
    return __import__("pprint").pprint(data)


def save_file(output_file: str, data: str):
    # Ensure parent dir exists.
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as file:
        file.write(data)

    Log.info("Rendered file saved to %s", output_file)

    # Print clickable file URL for HTML files
    if output_file.endswith(".html"):
        abs_path = os.path.abspath(output_file)
        Log.info(f"Link: file://{abs_path}")
