SELECT books.book_id,
       books.title,
       books.year,
       events.event_id,
       events.event
FROM books
JOIN book_authors ON books.book_id = book_authors.book_id
JOIN authors ON book_authors.author_id = authors.author_id
JOIN events ON events.book_id = books.book_id
WHERE authors.author_id = 12
ORDER BY books.year;
