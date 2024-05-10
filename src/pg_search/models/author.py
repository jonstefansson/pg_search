from dataclasses import dataclass


@dataclass
class Author:
    author_id: int
    name_first: str
    name_last: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            author_id=data['author_id'],
            name_first=data['name_first'],
            name_last=data['name_last']
        )
