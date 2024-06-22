from dataclasses import dataclass, field
from ..support import get_template


@dataclass
class Author:
    author_id: int
    name_first: str
    name_last: str
    year: int = field(default=0)

    @classmethod
    def from_dict(cls, data):
        return cls(
            author_id=data['author_id'],
            name_first=data['name_first'],
            name_last=data['name_last'],
            year=data['year']
        )

    @classmethod
    def find_or_create(cls, ctx, author: 'Author') -> 'Author':
        """
        Find an author by author_id or create a new author.

        Note that I have to use the string 'Author' in the type hint because
        the class Author is not defined until after the class is defined.

        :param ctx:
        :param author:
        :return:
        """
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            """
            SELECT author_id, name_last, name_first, year
            FROM authors
            WHERE name_last = %s AND name_first = %s AND year = %s;
            """,
            (author.name_last, author.name_first, author.year)
        )
        record = cur.fetchone()
        if record:
            return cls(*record)
        else:
            cur = conn.execute(
                """
                INSERT INTO authors (name_last, name_first, year)
                VALUES (%s, %s, %s)
                RETURNING author_id
                """,
                (author.name_last, author.name_first, author.year)
            )
            author_id = cur.fetchone()[0]
        return cls(author_id, author.name_last, author.name_first, author.year)

    @classmethod
    def book_authors(cls, ctx, book_id):
        template = get_template('book_authors.sql')
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            template.render(),
            (book_id,)
        )
        return [cls(*record) for record in cur]
