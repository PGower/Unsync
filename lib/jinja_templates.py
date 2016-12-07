"""Jinja2 templating helpers."""
import os
from jinja2 import Environment, FileSystemLoader

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def template_env():
    """Create and return a simple Jinja2 template enviroment."""
    e = Environment(loader=FileSystemLoader(os.path.join(BASE_PATH, '../templates/')),
                    trim_blocks=True)
    return e


def render(template_name, context={}):
    """Render the given template using the created enviromnent and passed context."""
    e = template_env()
    t = e.get_template(template_name)
    return t.render(**context)
