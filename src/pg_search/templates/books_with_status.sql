-- -----------------------------------------------------------------------------
-- Lists all books with given current event status.
-- -----------------------------------------------------------------------------
SELECT books.book_id,
       books.title,
       authors.name_last || ', ' || authors.name_first as author,
       events.event,
       to_char(events.created_at, 'YYYY-MM-DD HH24:MI') as created_at
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
GROUP BY books.book_id, authors.author_id, events.event_id
HAVING events.event = %(status)s
ORDER BY events.created_at DESC;
