SELECT id,
       title,
       title_full,
       tags,
       status,
       series_rank,
       year,
       searchable
FROM books
WHERE id = %s;
