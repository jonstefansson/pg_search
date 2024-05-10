import psycopg


def insert_book(data):
    with psycopg.connect("host=localhost dbname=pgsearch user=boston") as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, tags, series_rank)
                VALUES (%(title)s, %(tags)s, %(series_rank)s)
                RETURNING book_id
                """,
                data
            )
