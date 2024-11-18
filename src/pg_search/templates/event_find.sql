SELECT id, book_id, event, created_at
FROM events
WHERE booK_id = %s AND event = %s;
