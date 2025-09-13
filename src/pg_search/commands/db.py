import logging

import click
import json
from pg_search.services.yaml_loader import load_yaml
from pg_search.database import DatabaseConnection, Query
from ..models import Book, Event, EventEnum
from ..support import get_template, safe_parse
from dataclasses import asdict
from ..support.json import CustomJsonEncoder


@click.group()
@click.pass_context
def db_cli(ctx):
    ctx.ensure_object(dict)
    db = DatabaseConnection('postgresql://boston@localhost/pgsearch')
    ctx.obj['db'] = db

    @ctx.call_on_close
    def close_connection():
        """
        Automatically closes the database connection when the command completes.

        :return:
        """
        db.get_connection().close()
        logging.getLogger('pg_search.db').info('database connection closed')


@db_cli.command('book-activity')
@click.pass_context
@click.argument('book_id', type=click.INT, required=True)
def book_activity(ctx, book_id):
    """
    Show event history of a book.

    :param ctx:
    :param book_id:
    :return:
    """
    book, events = Book.activity(ctx, book_id)
    result = dict(
        book=asdict(book),
        events=[asdict(e) for e in events]
    )
    click.echo(json.dumps(result, cls=CustomJsonEncoder))

@db_cli.command('find-book')
@click.pass_context
@click.argument('book_id', required=True, type=click.INT)
def find_book_by_id(ctx, book_id):
    """
    Finds a book by its book_id.

    :param ctx: dict -- the click context
    :param book_id: int -- the book_id
    :return:
    """
    book = Book.find_by_id(ctx, book_id)
    if book is not None:
        click.echo(json.dumps(asdict(book), cls=CustomJsonEncoder))
    else:
        click.secho(f"Book {book_id} not found", err=True, fg='red')


@db_cli.command('authors')
@click.pass_context
def authors(ctx):
    """
    Lists authors in the database.

    :param ctx: dict -- the click context
    :return:
    """
    conn = ctx.obj['db'].get_connection()
    with conn.execute(
        """
        SELECT id, name_last, name_first
        FROM authors
        """
    ) as cur:
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
        ctx.obj['db'].get_connection().commit()
        logging.getLogger('pg_search.db').info('transaction committed')
        click.echo(json.dumps(result, cls=CustomJsonEncoder))


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
@click.argument("book_id", type=click.INT)
@click.pass_context
def build_searchable(ctx, book_id):
    """
    Updates the searchable column for a book.

    :param ctx: dict -- the click context
    :param book_id: int -- the book_id
    :return:
    """
    Book.update_searchable(ctx, book_id)
    click.echo(f"Updated searchable column for Book {book_id}", err=True)


@db_cli.command('reindex')
@click.pass_context
def reindex(ctx):
    """
    Rebuilds the idx_searchable_book index.

    :param ctx: dict -- the click context
    :return:
    """
    conn = ctx.obj['db'].get_connection()
    conn.execute(
        get_template('reindex.sql').render()
    )
    click.secho('Reindexed idx_searchable_book', err=True, fg='green')


@db_cli.command('add-event')
@click.pass_context
@click.option("-i", "--id", "book_id", help="The book_id", required=True, type=click.INT)
@click.option("-e", "--event", "event", help="The event enum", required=True, type=click.Choice([str(i) for i in EventEnum]))
@click.option("-c", "--created_at", "created_at", help="The date (defaults to today)", required=False, type=click.STRING)
def add_event(ctx, book_id, event, created_at):
    """
    Adds an event to the database.

    :param ctx: dict -- the click context
    :param book_id: int --
    :param event: str -- the event enum
    :param created_at: datetime -- the date of the event
    :return:
    """
    Event.find_or_create(
        ctx,
        event=Event.from_dict(
            dict(
                id=None,
                book_id=book_id,
                event=event,
                created_at=safe_parse(created_at)
            )
        )
    )
    Book.update_status(ctx, book_id, event)


@db_cli.command('search')
@click.option(
    '-p',
    '--query-parser',
    'query_parser',
    help='The query parser to use',
    required=False,
    default='websearch_to_tsquery',
    type=click.Choice(
        [
            'to_tsquery',
            'plainto_tsquery',
            'phraseto_tsquery',
            'websearch_to_tsquery'
        ]
    )
)
@click.option('-s', '--status', 'status', required=False, default='ALL', type=click.Choice(['ALL'] + [str(i) for i in EventEnum]))
@click.argument('query', required=True, type=click.STRING)
@click.pass_context
def search(ctx, status, query, query_parser):
    """
    Full-text search for books and authors.

    :param ctx: dict -- the click context
    :param status: str -- the status enum
    :param query: str -- the search query
    :param query_parser: str -- the query parser
    :return:
    """
    from tabulate import tabulate
    book_tuples = [book_tuple for book_tuple in Book.search(ctx, status, query, query_parser)]
    click.echo(tabulate(book_tuples, headers=[
        'book_id',
        'title',
        'year',
        'series_rank',
        'status',
        'author'
    ]))


@db_cli.command('book-status')
@click.argument('status', required=True, type=click.Choice([str(i) for i in EventEnum]))
@click.pass_context
def book_status(ctx, status):
    """
    Lists books with status passed as argument.

    :param ctx:
    :param status:
    :return:
    """
    from tabulate import tabulate
    conn = ctx.obj['db'].get_connection()
    query = Query(
        template_name='books_with_status.sql',
        template_params=dict(),
        query_params=dict(status=status),
        fetch_one=False
    )
    results = query.execute(conn)
    click.echo(
        tabulate(results, headers=[
            'book_id',
            'title',
            'authors',
            'status',
            'created_at'
        ]))
