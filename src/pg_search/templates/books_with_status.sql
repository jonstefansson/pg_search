-- -----------------------------------------------------------------------------
-- Lists all books with given current event status.
-- -----------------------------------------------------------------------------
SELECT books.id,
       books.title,
       books.status,
       array_agg(authors.name_last || ', ' || authors.name_first) as author
FROM books
JOIN book_authors ON books.id = book_authors.book_id
JOIN authors ON book_authors.author_id = authors.id
WHERE books.status = %(status)s
GROUP BY books.id
ORDER BY books.id DESC;
