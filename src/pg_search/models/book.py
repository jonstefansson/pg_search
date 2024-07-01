import logging
from dataclasses import dataclass, field, asdict
from ..support import get_template


@dataclass
class Book:
    book_id: int
    title: str
    title_full: str
    tags: list[str]
    authors: list['Author'] = field(default_factory=list)
    last_event: 'Event' = None
    series_rank: int = 0
    year: int = 0

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_id=data['book_id'],
            title=data['title'],
            title_full=data['title_full'],
            tags=data['tags'],
            series_rank=data['series_rank'],
            year=data['year']
        )

    def associate_author(self, ctx, author: 'Author'):
        conn = ctx.obj['db'].get_connection()
        with conn.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM book_authors
                WHERE book_authors.book_id = %s AND book_authors.author_id = %s
            ) 
            """,
            (self.book_id, author.author_id)
        ) as cur:
            if not cur.fetchone()[0]:
                conn.execute(
                    """
                    INSERT INTO book_authors (book_id, author_id)
                    VALUES (%s, %s);
                    """,
                    (self.book_id, author.author_id)
                )

    @classmethod
    def find_by_id(cls, ctx, book_id):
        from ..models import Author, Event
        book = None
        template = get_template('book_find_by_id.sql')
        conn = ctx.obj['db'].get_connection()
        with conn.execute(
            template.render(),
            (book_id,)
        ) as cur:
            record = cur.fetchone()
            if record:
                book = cls(
                    book_id=record[0],
                    title=record[1],
                    title_full=record[2],
                    tags=record[3],
                    series_rank=record[4],
                    year=record[5]
                )
                book.authors = [author for author in Author.book_authors(ctx, book_id)]
                book.last_event = Event.last_event(ctx, book_id)
        return book

    @classmethod
    def find_or_create(cls, ctx, book: 'Book') -> 'Book':
        conn = ctx.obj['db'].get_connection()
        with conn.execute(
            """
            SELECT book_id, title, title_full, tags, series_rank
            FROM books
            WHERE title = %s AND year = %s;
            """,
            (book.title, book.year)
        ) as cur:
            record = cur.fetchone()
        if record:
            return cls(*record)
        with conn.execute(
            """
            INSERT INTO books (title, title_full, tags, series_rank, year)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING book_id
            """,
            (book.title, book.title_full, book.tags, book.series_rank, book.year)
        ) as cur:
            book_id = cur.fetchone()[0]
            book = cls(book_id, book.title, book.title_full, book.tags, book.series_rank)
            conn.commit()
            return book

    @staticmethod
    def insert_book(ctx, data_dict):
        """
        Inserts a book into the database.
        :param ctx:
        :param data_dict: See payloads/book.yml for structure
        :return:
        """
        from pg_search.models import Author, Book, Event
        logging.getLogger('pg_search.models.book').info(f"insert_book -- data_dict: {data_dict}")
        authors = [Author.find_or_create(ctx, author) for author in data_dict['authors']]
        data_dict['authors'] = authors
        book = Book.find_or_create(ctx, data_dict['book'])
        data_dict['book'] = book
        for author in authors:
            book.associate_author(ctx, author)
        data_dict['event'].book_id = book.book_id
        event = Event.find_or_create(ctx, data_dict['event'])
        Book.update_searchable(ctx, book.book_id)
        return dict(authors=[asdict(a) for a in authors], book=asdict(book), event=asdict(event))

    @staticmethod
    def update_searchable(ctx, book_id):
        """
        Updates the searchable column of the books table. Remember to reindex the searchable index after making a change.
        :param ctx:
        :param book_id:
        :return:
        """
        template = get_template('update_book_searchable.sql')
        conn = ctx.obj['db'].get_connection()
        conn.execute(
            template.render(),
            dict(book_id=book_id)
        )
        conn.commit()

    @staticmethod
    def search(ctx, query):
        """
        Performs full-text search on books and authors.

        :param ctx: dict -- the click context
        :param query: str -- the search term
        :return:
        """
        template = get_template('search.sql')
        conn = ctx.obj['db'].get_connection()
        with conn.execute(
            template.render(),
            dict(query=query)
        ) as cur:
            for record_tuple in cur:
                yield record_tuple
