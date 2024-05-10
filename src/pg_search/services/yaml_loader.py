import yaml
from pg_search.models.author import Author
from pg_search.models.book import Book
from pg_search.models.event import Event


def load_yaml(input_stream):
    data = yaml.safe_load(input_stream)
    return dict(
        book=Book.from_dict(data['book']),
        author=Author.from_dict(data['author']),
        event=Event.from_dict(data['event'])
    )
