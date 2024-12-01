import click
import json
from ..support import get_template


@click.group()
def tools_cli():
    pass


@tools_cli.command("pipe-to-table")
@click.argument('finput', required=True, type=click.File('rt'))
@click.option(
    '-t',
    '--tablefmt',
    'tablefmt',
    help='tabulate format',
    default='simple',
    type=click.Choice(['plain', 'simple', 'github', 'jira', 'pipe', 'psql', 'grid', 'simple_grid', 'simple_outline'])
)
def pipe_to_table(finput, tablefmt):
    """
    Splits lines by pipe character; displays table.

    :param finput:
    :param tablefmt:
    :return:
    """
    import re
    from tabulate import tabulate

    columns = []
    for line in finput:
        values = re.split(r'\s*\|\s*', line.strip())
        columns.append(values)
    click.echo(tabulate(columns, headers="firstrow", tablefmt=tablefmt))

@tools_cli.command('template')
@click.argument('json_input', required=True, type=click.File('rt'))
def template(json_input):
    """
    Renders a template file using template file name and template parameters
    found in JSON input.

    {
        "name": "search.sql",
        "parameters": {
            "query_parser": "websearch_to_tsquery"
        }
    }

    :param json_input:
    :return:
    """
    data = json.load(json_input)
    template_name = data.get('name')
    template_params = data.get('parameters')
    click.echo(get_template(template_name).render(template_params))
