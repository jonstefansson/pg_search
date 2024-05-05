CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    series_rank INTEGER DEFAULT 0,
    tags text[],
    title text NOT NULL
);

CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name_first text,
    name_last text NOT NULL
);

CREATE UNIQUE INDEX index_author_names ON authors (name_last, name_first);

CREATE TYPE event_type AS ENUM (
    'finished', 'reading', 'aborted', 'purchased',
    'pre-ordered', 'wished-for'
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    book_id INTEGER,
    event event_type NOT NULL,
    created_at date,
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
