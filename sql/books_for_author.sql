select books.book_id,
       books.title,
       books.series_rank,
       books.status,
       array_agg(authors.name_last || ', ' || authors.name_first) as authors
from books
join book_authors on books.book_id = book_authors.book_id
join authors on authors.author_id = book_authors.author_id
where authors.name_last = 'Connelly'
group by books.book_id, books.series_rank, authors.author_id
order by authors.author_id, books.series_rank;
