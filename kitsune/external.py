from dataclasses import dataclass
from datetime import datetime as dt

from kitsune.gallery import Gallery


@dataclass(frozen=True, slots=True)
class User:
    """User parsing class."""

    id: int
    username: str
    slug: str
    avatar_url: str
    is_superuser: bool
    is_staff: bool


@dataclass(frozen=True, slots=True)
class Comment:
    """Comments parsing class."""

    id: int
    gallery_id: int
    poster: User
    post_date: dt
    body: str


@dataclass(frozen=True, slots=True)
class Homepage:
    """Homepage parsing class."""

    trending_new: list[Gallery]
    new: list[Gallery]
