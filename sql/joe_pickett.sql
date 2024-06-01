SELECT book_id, title
FROM books
WHERE 'Joe Pickett' = ANY (tags);