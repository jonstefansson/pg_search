UPDATE books
SET searchable = (
  setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
  setweight(to_tsvector('english', COALESCE(title_full, '')), 'B') ||
  setweight(to_tsvector('english', array_to_string(tags, ' ')), 'C') ||
  (
      SELECT
          setweight(to_tsvector('english', string_agg(COALESCE(name_first, ''), ' ')),'B') ||
          setweight(to_tsvector('english', string_agg(COALESCE(name_last, ''), ' ')), 'A')
      FROM authors
      JOIN book_authors ON authors.author_id = book_authors.author_id
      WHERE book_authors.book_id = books.book_id
      GROUP BY book_authors.book_id
  )
);