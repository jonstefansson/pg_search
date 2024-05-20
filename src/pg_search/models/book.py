import logging
from dataclasses import dataclass
from pg_search.models.author import Author


@dataclass
class Book:
    book_id: int
    title: str
    tags: list[str]
    series_rank: int = 0
    year: int = 0

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_id=data['book_id'],
            title=data['title'],
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
    def find_or_create(cls, ctx, book: 'Book') -> 'Book':
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            """
            SELECT book_id, title, tags, series_rank
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
                INSERT INTO books (title, tags, series_rank, year)
                VALUES (%s, %s, %s, %s)
                RETURNING book_id
                """,
                (book.title, book.tags, book.series_rank, book.year)
            )
            book_id = cur.fetchone()[0]
        return cls(book_id, book.title, book.tags, book.series_rank)

    @staticmethod
    def insert_book(ctx, data_dict):
        from pg_search.models import Author, Book, Event
        logging.getLogger('pg_search.models.book').info(f"insert_book -- data_dict: {data_dict}")
        author = Author.find_or_create(ctx, data_dict['author'])
        data_dict['author'] = author
        book = Book.find_or_create(ctx, data_dict['book'])
        data_dict['book'] = book
        book.associate_author(ctx, author)
        event = Event.find_or_create(ctx, data_dict['event'], book)
        return dict(author=author, book=book, event=event)
