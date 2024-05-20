import logging
from dataclasses import dataclass
from datetime import datetime
from pg_search.support.date import safe_parse, current_timestamp_callable
from pg_search.models import Book


@dataclass
class Event:
    event_id: int
    book_id: int
    event: str
    created_at: datetime

    @classmethod
    def from_dict(cls, data):
        return cls(
            event_id=data['event_id'],
            book_id=data['book_id'],
            event=data['event'],
            created_at=safe_parse(data['created_at'])
        )

    @classmethod
    def find_or_create(cls, ctx, event: 'Event', book: 'Book') -> 'Event':
        db = ctx.obj['db']
        conn = db.get_connection()
        cur = conn.execute(
            """
            SELECT event_id, book_id, event, created_at
            FROM events
            WHERE book_id = %s AND event = %s;
            """,
            (book.book_id, event.event)
        )
        record = cur.fetchone()
        if record:
            return cls(*record)

        cur = conn.execute(
            """
            INSERT INTO events (book_id, event, created_at)
            VALUES (%s, %s, %s)
            RETURNING event_id, book_id
            """,
            (
                book.book_id,
                event.event,
                safe_parse(
                    date_expression=event.created_at,
                    default=current_timestamp_callable
                )
            )
        )
        event_id, book_id = cur.fetchone()

        logging.getLogger('pg_search.models.event').info(f"insert event -- event_id: {event_id}")
        return cls(event_id, book_id, event.event, event.created_at)
