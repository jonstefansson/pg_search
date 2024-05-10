import click
from pg_search.services.yaml_loader import load_yaml
from pg_search.database import DatabaseConnection


@click.group()
def db_cli():
    pass


@db_cli.command('authors')
def authors():
    db = DatabaseConnection('postgresql://boston@localhost/pgsearch')
    with db.get_connection() as conn:
        cur = conn.execute("""\
        SELECT author_id, name_last, name_first
        FROM authors
        """)
        for record in cur:
            click.echo(record)


@db_cli.command('insert-book')
@click.argument('yml_input', required=True, type=click.File('r'))
def insert_book(yml_input):
    data_dict = load_yaml(yml_input)
    click.echo(data_dict)
