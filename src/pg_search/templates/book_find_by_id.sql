SELECT book_id, title, title_full, tags, series_rank
FROM books
WHERE book_id = %s;
