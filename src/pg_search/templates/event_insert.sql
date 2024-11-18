INSERT INTO events (book_id, event, created_at)
VALUES (%s, %s, %s)
RETURNING id, book_id;
