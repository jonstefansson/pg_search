INSERT INTO events (book_id, event, created_at)
VALUES (%s, %s, %s)
RETURNING event_id, book_id;
