import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils.logging import Log

jinja = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())


#
# Simple general-purpose renderers for the most basic formats.
#


def render_html(data, template_path: str):
    template = jinja.get_template(template_path)
    return template.render(data=data)


def render_json(data):
    return json.dumps(data, indent=2)


def render_stdout(data):
    return __import__("pprint").pprint(data)


def save_file(output_file: str, data: str):
    with open(output_file, "w") as file:
        file.write(data)

    Log.info("Rendered file saved to %s", output_file)