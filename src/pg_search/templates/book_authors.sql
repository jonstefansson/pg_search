SELECT authors.author_id,
       authors.name_first,
       authors.name_last,
       authors.year
FROM authors
JOIN book_authors ON authors.author_id = book_authors.author_id
WHERE book_authors.book_id = %s;
