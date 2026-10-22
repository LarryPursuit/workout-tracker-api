"""Small checks shared by the models' @validates hooks."""
from typing import Optional


def require_positive_int(key: str, value, maximum: Optional[int] = None) -> int:
    # bool is a subclass of int, so True would otherwise pass as 1.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be a whole number.")
    if value <= 0:
        raise ValueError(f"{key} must be greater than 0.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{key} must be at most {maximum}.")
    return value


def optional_positive_int(key: str, value, maximum: Optional[int] = None) -> Optional[int]:
    if value is None:
        return None
    return require_positive_int(key, value, maximum)
