import yaml
from pg_search.models.author import Author
from pg_search.models.book import Book
from pg_search.models.event import Event


def load_yaml(input_stream):
    data_list = yaml.safe_load(input_stream)
    return [
        dict(
            book=Book.from_dict(data['book']),
            authors=[Author.from_dict(author) for author in data['authors']],
            event=Event.from_dict(data['event'])
        )
        for data in data_list
    ]
