SELECT book_id,
       title,
       year
FROM books
WHERE searchable IS NULL;
