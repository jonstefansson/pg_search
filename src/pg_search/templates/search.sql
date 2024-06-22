SELECT books.book_id,
       books.title,
       string_agg((authors.name_last || ', ' || authors.name_first), ', ') as author
FROM books
LEFT JOIN book_authors ON books.book_id = book_authors.book_id
LEFT JOIN authors ON book_authors.author_id = authors.author_id
WHERE books.searchable @@ websearch_to_tsquery('english', %s)
GROUP BY authors.author_id, books.book_id
ORDER BY authors.author_id;
