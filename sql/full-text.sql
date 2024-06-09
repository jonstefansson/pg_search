-- -----------------------------------------------------------------------------
-- If you are searching columns in the same table, you can define a generated
-- column, which will update itself when the columns it depends on are updated.
--
-- But you cannot do this and join columns from other tables.
-- -----------------------------------------------------------------------------
ALTER TABLE books
ADD COLUMN searchable_book_docs tsvector GENERATED ALWAYS AS (
	setweight(to_tsvector('english', COALESCE(title, ''), 'A')) ||
	setweight(to_tsvector('english', COALESCE(title_full, ''), 'B'))
) STORED;
CREATE INDEX idx_searchable_book_docs ON books USING GIN(searchable_book_docs);

-- -----------------------------------------------------------------------------
-- If you need to join columns from other tables, you can create a trigger
-- -----------------------------------------------------------------------------
ALTER TABLE books ADD COLUMN searchable_book_docs tsvector;

-- Step 2: Update the new column with the tsvector of the data from the joined table
UPDATE books
SET searchable_book_docs = to_tsvector('english', authors.name_last || ', ' || authors.name_first)
FROM book_authors
JOIN authors ON book_authors.author_id = authors.author_id
WHERE books.book_id = book_authors.book_id;

CREATE INDEX books_searchable_full_name_idx ON books USING gin(searchable_full_name);