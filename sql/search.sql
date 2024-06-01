-- -----------------------------------------------------------------------------
-- https://www.postgresql.org/docs/16/textsearch-tables.html#TEXTSEARCH-TABLES-SEARCH
-- 
-- Need to figure out how to search text[] column.
-- ERROR:  function to_tsvector(unknown, text[]) does not exist
-- LINE 3: WHERE to_tsvector('english', tags) @@ to_tsquery('english', ...
-- 
-- Here's an interesting solution for full text search on multiple tables:
-- https://stackoverflow.com/questions/45123689/can-a-view-of-multiple-tables-be-used-for-full-text-search
-- -----------------------------------------------------------------------------
SELECT book_id, title
FROM books
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'Demon');


SELECT title
FROM books
WHERE to_tsvector(title || ' ' || body) @@ to_tsquery('create & table')
ORDER BY last_mod_date DESC
LIMIT 10;

SELECT books.title || ' ' || books.title_full
FROM books
JOIN book_authors ON books.book_id = book_authors


-- -----------------------------------------------------------------------------
-- https://dba.stackexchange.com/questions/107801/full-text-search-on-multiple-joined-tables
-- Note how the joins are constructed. What does USING (id) mean?
-- 
-- USING ( join_column [, ...] ) [ AS join_using_alias ]
-- A clause of the form USING ( a, b, ... ) is shorthand for ON left_table.a = 
-- right_table.a AND left_table.b = right_table.b .... Also, USING implies that only one 
-- of each pair of equivalent columns will be included in the join output, not both.

-- If a join_using_alias name is specified, it provides a table alias for the join 
-- columns. Only the join columns listed in the USING clause are addressable by this 
-- name. Unlike a regular alias, this does not hide the names of the joined tables from 
-- the rest of the query. Also unlike a regular alias, you cannot write a column alias 
-- list — the output names of the join columns are the same as they appear in the USING 
-- list.
-- https://www.postgresql.org/docs/16/sql-select.html
-- -----------------------------------------------------------------------------
SELECT a.article_title AS title
FROM   article a
LEFT   JOIN (
   SELECT x.article_id AS id, string_agg(y.keyword, ' ') AS txt
   FROM   article_keywords x
   JOIN   keyword          y ON y.id = x.keyword_id
   GROUP  BY 1
   ) k USING (id)
LEFT   JOIN (
   SELECT x.article_id AS id, string_agg(y.name, ' ') AS txt
   FROM   article_authors x
   JOIN   author          y ON y.id = x.author_id
   GROUP  BY 1
   ) a USING (id)
LEFT   JOIN (
   SELECT x.article_id AS id, string_agg(y.org_name, ' ') AS txt
   FROM   article_organisations x
   JOIN   organisation          y ON y.id = x.organisation_id
   GROUP  BY 1
   ) o USING (id)
WHERE  to_tsvector(concat_ws(' ', a.article_title, k.txt, a.txt, o.txt))
    @@ to_tsquery('David & Feeney');


-- -----------------------------------------------------------------------------
-- github copilot result
-- Create an index on the 'title' column of the 'books' table
-- -----------------------------------------------------------------------------
CREATE INDEX books_title_idx ON books USING gin(to_tsvector('english', title));
-- Perform a full text search for 'python'
SELECT title FROM books WHERE to_tsvector('english', title) @@ to_tsquery('english', 'python');
