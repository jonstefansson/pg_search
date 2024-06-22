-- -----------------------------------------------------------------------------
-- AI generated content.
--
-- If you are searching columns in the same table, you can define a generated
-- column, which will update itself when the columns it depends on are updated.
--
-- But you cannot do this and join columns from other tables.
--
-- setweight weights are ranked from highest to lowest as follows: A > B > C > D.
--
-- Note the use of COALESCE to handle NULL values. This is a best practice.
-- -----------------------------------------------------------------------------
-- ALTER TABLE books
-- ADD COLUMN searchable tsvector GENERATED ALWAYS AS (
-- 	setweight(to_tsvector('english', COALESCE(title, ''), 'B')) ||
-- 	setweight(to_tsvector('english', COALESCE(title_full, ''), 'A'))
-- ) STORED;
-- CREATE INDEX idx_searchable_book ON books USING GIN(searchable);

-- -----------------------------------------------------------------------------
-- If you need to join columns from other tables, you can create a trigger
-- -----------------------------------------------------------------------------
ALTER TABLE books
ADD IF NOT EXISTS searchable tsvector;

-- Step 1: Create a function for the books table
CREATE OR REPLACE FUNCTION update_books_searchable() RETURNS TRIGGER AS $$
BEGIN
  NEW.searchable := (
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.title_full, '')), 'B') ||
    setweight(to_tsvector('english', array_to_string(NEW.tags, ' ')), 'C') ||
    (
        SELECT
            setweight(to_tsvector('english', COALESCE(name_first, '')),'B') ||
            setweight(to_tsvector('english', COALESCE(name_last, '')), 'A')
        FROM authors
        JOIN book_authors ON authors.author_id = book_authors.author_id
        WHERE book_authors.book_id = NEW.book_id
    )
  );
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Step 2: Create a trigger for the books table
CREATE TRIGGER update_books_searchable_trigger
BEFORE INSERT OR UPDATE ON books
FOR EACH ROW EXECUTE FUNCTION update_books_searchable();

-- Step 3: Create a function for the authors table
CREATE OR REPLACE FUNCTION update_authors_searchable() RETURNS TRIGGER AS $$
BEGIN
  UPDATE books
  SET searchable = (
    setweight(to_tsvector('english', COALESCE(NEW.name_first, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(NEW.name_last, '')), 'A') ||
    (
        SELECT setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
               setweight(to_tsvector('english', COALESCE(title_full, '')), 'B') ||
               setweight(to_tsvector('english', array_to_string(tags, ' ')), 'C')
        FROM books
        JOIN book_authors ON book_authors.book_id = books.book_id
        WHERE book_authors.author_id = NEW.author_id
    )
  )
  WHERE author_id = NEW.author_id;
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Step 4: Create a trigger for the authors table
CREATE TRIGGER update_authors_searchable_trigger
AFTER UPDATE ON authors
FOR EACH ROW EXECUTE FUNCTION update_authors_searchable();

-- -----------------------------------------------------------------------------
-- Force Postgres to rebuild an index with this command. A reindex can take
-- a long time and consume considerable resources depending on the size of the
-- table and the index.
-- -----------------------------------------------------------------------------
-- REINDEX INDEX your_index_name;
