SELECT event_id, book_id, event, created_at
FROM events
WHERE book_id = %s AND event = %s;
