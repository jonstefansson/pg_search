import logging
import click
from pg_search.services.yaml_loader import load_yaml
from pg_search.database import DatabaseConnection
from pg_search.models import Book


@click.group()
@click.pass_context
def db_cli(ctx):
    ctx.ensure_object(dict)
    db = DatabaseConnection('postgresql://boston@localhost/pgsearch')
    ctx.obj['db'] = db

    @ctx.call_on_close
    def close_connection():
        db.get_connection().close()
        logging.getLogger('pg_search.db').info('database connection closed')


@db_cli.command('authors')
@click.pass_context
def authors(ctx):
    db = ctx.obj['db']
    cur = db.get_connection().execute(
        """
        SELECT author_id, name_last, name_first
        FROM authors
        """
    )
    for record in cur:
        click.echo(record)


@db_cli.command('insert-books')
@click.argument('yml_input', required=True, type=click.File('r'))
@click.pass_context
def insert_books(ctx, yml_input):
    books = load_yaml(yml_input)
    for data_dict in books:
        result = Book.insert_book(ctx, data_dict)
        logging.getLogger('pg_search.commands.db').info(f"result: {result}")
        ctx.obj['db'].get_connection().commit()
        logging.getLogger('pg_search.db').info('transaction committed')


@db_cli.command('prepare')
@click.argument('yml_input', required=True, type=click.File('r'))
def prepare(yml_input):
    import yaml
    from jinja2 import Environment, PackageLoader, select_autoescape
    from datetime import date
    env = Environment(
        loader=PackageLoader("pg_search", "templates"),
        autoescape=select_autoescape()
    )
    data = yaml.safe_load(yml_input)
    for book in data:
        template = env.get_template('book_yaml.j2')
        click.echo(template.render(
            title=book['title'],
            rank=book['rank'],
            year=book['year'],
            created_at=date(int(book['year']), 7, 4).isoformat()
        ))

