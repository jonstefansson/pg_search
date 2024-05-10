from dataclasses import dataclass
import datetime


@dataclass
class Event:
    event_id: int
    book_id: int
    event: str
    created_at: datetime.date = datetime.date.today()

    @classmethod
    def from_dict(cls, data):
        return cls(
            event_id=data['event_id'],
            book_id=data['book_id'],
            event=data['event'],
            created_at=data['created_at']
        )
