-- returns the last event for a given book_id
SELECT *
FROM events
WHERE book_id = %s
ORDER BY created_at DESC
LIMIT 1;