-- -----------------------------------------------------------------------------
-- Lists all books with given current event status.
-- -----------------------------------------------------------------------------
SELECT books.id,
       books.title,
       array_agg(authors.name_last || ', ' || authors.name_first) as author,
       events.event,
       to_char(events.created_at, 'YYYY-MM-DD HH24:MI') as created_at
FROM books
JOIN (
  SELECT book_id, MAX(created_at) as max_created_at
  FROM events
  GROUP BY book_id
) subquery ON books.id = subquery.book_id
JOIN events ON books.id = events.book_id
  AND events.created_at = subquery.max_created_at
JOIN book_authors ON books.id = book_authors.book_id
JOIN authors ON book_authors.author_id = authors.id
GROUP BY books.id, events.id
HAVING events.event = %(status)s
ORDER BY events.created_at DESC;
