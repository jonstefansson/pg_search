from dataclasses import dataclass


@dataclass
class Book:
    book_id: int
    title: str
    tags: list[str]
    series_rank: int = 0

    @classmethod
    def from_dict(cls, data):
        return cls(
            book_id=data['book_id'],
            title=data['title'],
            tags=data['tags'],
            series_rank=data['series_rank']
        )
