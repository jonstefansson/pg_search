-- 2024-08-04
-- ALTER TABLE books
-- ADD COLUMN last_event event_type NULL;
-- CREATE INDEX idx_last_event ON books (last_event);

ALTER TABLE books RENAME COLUMN last_event TO status;
ALTER INDEX idx_last_event RENAME TO idx_status;

-- 2024-08-04
-- populate books.status column with events table data
begin;
update books
set status = b.last_event
from (
    SELECT books.book_id,
           events.event as last_event
    FROM books
    JOIN (
      SELECT book_id, MAX(created_at) as max_created_at
      FROM events
      GROUP BY book_id
    ) subquery ON books.book_id = subquery.book_id
    JOIN events ON books.book_id = events.book_id
      AND events.created_at = subquery.max_created_at
    JOIN book_authors ON books.book_id = book_authors.book_id
    JOIN authors ON book_authors.author_id = authors.author_id
    GROUP BY books.book_id, events.event_id
) b
where books.book_id = b.book_id
returning books.book_id, books.status;
rollback;
