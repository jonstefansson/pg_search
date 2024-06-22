SELECT book_id,
       title,
       title_full,
       tags,
       series_rank,
       year,
       searchable
FROM books
WHERE book_id = %s;
