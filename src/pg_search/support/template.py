from jinja2 import Environment, PackageLoader, select_autoescape


def get_template(template_name: str) -> 'Template':
    env = Environment(
        loader=PackageLoader("pg_search", "templates"),
        autoescape=select_autoescape()
    )
    return env.get_template(template_name)
