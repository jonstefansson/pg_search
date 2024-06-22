import logging
import click
import yaml
from pg_search.services.yaml_loader import load_yaml
from pg_search.database import DatabaseConnection
from ..models import Book, Event
from ..support import get_template, safe_parse
from dataclasses import asdict


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


@db_cli.command('find-book')
@click.pass_context
@click.argument('book_id', required=True, type=int)
def find_book_by_id(ctx, book_id):
    """
    Finds a book by its book_id.
    :param ctx:
    :param book_id:
    :return:
    """
    book = Book.find_by_id(ctx, book_id)
    if book is not None:
        click.echo(yaml.dump(asdict(book)))
    else:
        click.secho(f"Book {book_id} not found", err=True, fg='red')


@db_cli.command('authors')
@click.pass_context
def authors(ctx):
    """
    Lists authors in the database.

    :param ctx:
    :return:
    """
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
    """
    Inserts one or more books in yml_input in the form of payloads/book.yml.
    :param ctx:
    :param yml_input:
    :return:
    """
    books = load_yaml(yml_input)
    for data_dict in books:
        result = Book.insert_book(ctx, data_dict)
        logging.getLogger('pg_search.commands.db').info(f"result: {result}")
        ctx.obj['db'].get_connection().commit()
        logging.getLogger('pg_search.db').info('transaction committed')


@db_cli.command('prepare')
@click.argument('yml_input', required=True, type=click.File('r'))
def prepare(yml_input):
    """
    This function takes a flat yaml file containing book data and emits structured yaml for use by insert_books.
    :param yml_input:
    :return:
    """
    import yaml
    from datetime import date
    data = yaml.safe_load(yml_input)
    for book in data:
        template = get_template('book_yaml.j2')
        click.echo(template.render(
            title=book['title'],
            rank=book['rank'],
            year=book['year'],
            created_at=date(int(book['year']), 7, 4).isoformat()
        ))


@db_cli.command('build-searchable')
@click.option("-i", "--id", "book_id", help="The book_id", type=click.INT)
@click.pass_context
def build_searchable(ctx, book_id):
    Book.update_searchable(ctx, book_id)
    click.echo(f"Updated searchable column for Book {book_id}", err=True)


@db_cli.command('reindex')
@click.pass_context
def reindex(ctx):
    db = ctx.obj['db']
    conn = db.get_connection()
    conn.execute(
        get_template('reindex.sql').render()
    )
    click.secho('Rebuilt idx_searchable_book', err=True, fg='green')


@db_cli.command('add-event')
@click.pass_context
@click.option("-i", "--id", "book_id", help="The book_id", required=True, type=click.INT)
@click.option("-e", "--event", "event", help="The event enum", required=True, type=click.STRING)
@click.option("-c", "--created_at", "created_at", help="The date (defaults to today)", required=False, type=click.STRING)
def add_event(ctx, book_id, event, created_at):
    Event.find_or_create(
        ctx,
        event=Event.from_dict(
            dict(
                event_id=None,
                book_id=book_id,
                event=event,
                created_at=safe_parse(created_at)
            )
        )
    )
