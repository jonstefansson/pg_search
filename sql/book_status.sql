-- -----------------------------------------------------------------------------
-- Lists all books with last event status.
-- -----------------------------------------------------------------------------
SELECT books.book_id,
       books.title,
       events.event,
       events.created_at
FROM books
JOIN (
  SELECT book_id, MAX(created_at) as max_created_at
  FROM events
  GROUP BY book_id
) subquery ON books.book_id = subquery.book_id
JOIN events ON books.book_id = events.book_id
  AND events.created_at = subquery.max_created_at;
