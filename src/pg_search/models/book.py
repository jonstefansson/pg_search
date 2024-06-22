import logging
from dataclasses import dataclass, field
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
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM book_authors
                WHERE book_authors.book_id = %s AND book_authors.author_id = %s
            ) 
            """,
            (self.book_id, author.author_id)
        )
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
        template = get_template('book_find_by_id.sql')
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            template.render(),
            (book_id,)
        )
        record = cur.fetchone()
        if record:
            book = cls(*record)
            book.authors = Author.book_authors(ctx, book_id)
            book.last_event = Event.last_event(ctx, book_id)
            return book
        return None

    @classmethod
    def find_or_create(cls, ctx, book: 'Book') -> 'Book':
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            """
            SELECT book_id, title, title_full, tags, series_rank
            FROM books
            WHERE title = %s AND year = %s;
            """,
            (book.title, book.year)
        )
        record = cur.fetchone()
        if record:
            return cls(*record)
        else:
            cur = conn.execute(
                """
                INSERT INTO books (title, title_full, tags, series_rank, year)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING book_id
                """,
                (book.title, book.title_full, book.tags, book.series_rank, book.year)
            )
            book_id = cur.fetchone()[0]
        return cls(book_id, book.title, book.title_full, book.tags, book.series_rank)

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
        author = Author.find_or_create(ctx, data_dict['author'])
        data_dict['author'] = author
        book = Book.find_or_create(ctx, data_dict['book'])
        data_dict['book'] = book
        book.associate_author(ctx, author)
        data_dict['event'].book_id = book.book_id
        event = Event.find_or_create(ctx, data_dict['event'])
        return dict(author=author, book=book, event=event)

    @staticmethod
    def update_searchable(ctx, book_id):
        """
        Updates the searchable column of the books table. Remember to reindex the searchable index after making a change.
        :param ctx:
        :param book_id:
        :return:
        """
        template = get_template('update_book_searchable.sql')
        db = ctx.obj['db']
        conn = db.get_connection()
        conn.execute(
            template.render(),
            book_id
        )
        conn.commit()
