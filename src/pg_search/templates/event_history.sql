SELECT events.*
FROM events
WHERE events.book_id = %s
ORDER BY events.created_at;
