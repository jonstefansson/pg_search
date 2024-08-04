CREATE TYPE event_type AS ENUM (
    'finished', 'reading', 'aborted', 'purchased',
    'pre-ordered', 'wished-for'
);

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    series_rank INTEGER DEFAULT 0,
    tags text[],
    title text NOT NULL,
    title_full text,
    year INTEGER NOT NULL DEFAULT 0,
    status event_type NULL,
    searchable tsvector
);

CREATE UNIQUE INDEX index_book_titles ON books (title, year);
CREATE INDEX idx_searchable_book ON books USING GIN(searchable);
CREATE INDEX idx_status ON books (status);

CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name_first text,
    name_last text NOT NULL,
    year INTEGER NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX index_author_names ON authors (name_last, name_first, year);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    book_id INTEGER,
    event event_type NOT NULL,
    created_at timestamp,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE UNIQUE INDEX index_book_events ON events (book_id, event);

CREATE TABLE book_authors (
    book_id INTEGER,
    author_id INTEGER,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
