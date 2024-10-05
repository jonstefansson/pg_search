SELECT books.book_id,
       books.title,
       books.year,
       books.series_rank,
       books.status,
       array_agg(format('%%s, %%s', authors.name_last, authors.name_first)) as author
FROM books
LEFT JOIN book_authors ON books.book_id = book_authors.book_id
LEFT JOIN authors ON book_authors.author_id = authors.author_id
WHERE books.searchable @@ {{ query_parser }}('english', %(query)s)
GROUP BY authors.author_id, books.book_id
ORDER BY authors.author_id, books.series_rank;
