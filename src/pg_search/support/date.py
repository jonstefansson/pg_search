from datetime import datetime, UTC
from typing import Optional, Callable, Union


def safe_parse(
        date_expression: Union[Optional[str], Optional[datetime]],
        default: Optional[Callable] = None
) -> Optional[datetime]:
    """
    Safely parse a date string or datetime instance. Allows a default value to be returned with a Callable.
    :param date_expression:
    :param default:
    :return:
    """
    try:
        match date_expression:
            case str() if isinstance(date_expression, str):
                _result = datetime.fromisoformat(date_expression)
            case datetime() if isinstance(date_expression, datetime):
                _result = date_expression
            case _:
                if default is not None:
                    _result = default()
                else:
                    _result = None
        return _result
    except (ValueError, TypeError) as e:
        return None


def current_timestamp_callable():
    return datetime.now(UTC)


def safe_iso_format(date: Optional[datetime]) -> Optional[str]:
    if date is None:
        return datetime.now(UTC).isoformat()
    else:
        return date.isoformat()
