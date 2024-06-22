SELECT authors.author_id, name_last, name_first
FROM authors
JOIN book_authors ON authors.author_id = book_authors.author_id
WHERE book_authors.book_id = %s;
