import logging
from dataclasses import dataclass
from datetime import datetime
from pg_search.support.date import safe_parse, current_timestamp_callable
from ..support import get_template


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
    def find_or_create(cls, ctx, event: 'Event') -> 'Event':
        conn = ctx.obj['db'].get_connection()
        with conn.execute(
            get_template('event_find.sql').render(),
            (event.book_id, event.event)
        ) as cur:
            record = cur.fetchone()
            if record:
                return cls(*record)

        with conn.execute(
            get_template('event_insert.sql').render(),
            (
                event.book_id,
                event.event,
                safe_parse(
                    date_expression=event.created_at,
                    default=current_timestamp_callable
                )
            )
        ) as cur:
            event_id, book_id = cur.fetchone()
        conn.commit()

        logging.getLogger('pg_search.models.event').info(f"insert event -- event_id: {event_id}")
        return cls(event_id, book_id, event.event, event.created_at)

    @classmethod
    def last_event(cls, ctx, book_id) -> 'Event':
        """
        Find the last event for a book.

        :param ctx: dict -- the click context
        :param book_id: int -- the book_id
        :return: Event
        """
        conn = ctx.obj['db'].get_connection()
        with conn.execute(
            get_template('event_last.sql').render(),
            (book_id,)
        ) as cur:
            record = cur.fetchone()
            if record:
                return cls(*record)
