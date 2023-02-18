from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timezone

__all__ = (
    "Title",
    "Tag",
    "Page",
    "Cover",
    "Thumb" "Gallery",
)


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
class Title:
    """Title parsing class."""

    english: str
    japanese: str
    pretty: str


@dataclass(frozen=True, slots=True)
class Tag:
    """Tag parsing class."""

    id: int
    type: str
    name: str
    url: str
    count: int


@dataclass(frozen=True, slots=True)
class Page:
    """Page parsing and image url parsing."""

    def __getitem__(self, key):
        return getattr(self, key)

    media_id: int
    num: int
    type: str
    resolution: tuple[int, int]

    @property
    def url(self) -> str:
        """Create page url for specified page."""
        return f"https://i.nhentai.net/galleries/{self.media_id}/{self.num}.{self.type}"


class Cover(Page):
    """Cover parsing and cover url."""

    @property
    def url(self) -> str:
        """Create cover url."""
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover.{self.type}"


class Thumb(Page):
    """Thumb parsing and thumbnail url."""

    @property
    def url(self) -> str:
        """Create thumbnail url."""
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{self.type}"


class Gallery:
    """Main parsing function."""

    EXTENSIONS = {"j": "jpg", "p": "png", "g": "gif"}

    def __init__(self, payload: dict):
        self.payload = payload

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def tags(self) -> list[Tag]:
        """Returns a list with metadata of all the tags of the doujin specified."""
        return [Tag(*tag.values()) for tag in self.payload["tags"]]

    @property
    def title(self) -> Title:
        """Returns the title in English, Japanese or Pretty, though it might not have the latter two."""
        return Title(*(self.payload["title"].values()))

    @property
    def pages(self) -> list[tuple[Page, str]]:
        """Returns a list of tuples, where 1st element of the tuple is metadata, and 2nd is the url."""
        pages = []

        for i in range(self.num_pages):
            entry = self.payload["images"]["pages"][i]

            page = Page(
                self.media_id,
                i + 1,
                self.EXTENSIONS[entry["t"]],
                (entry["w"], entry["h"]),
            )
            tup = (page, page.url)

            pages.append(tup)

        return pages

    @property
    def cover(self) -> tuple[Cover, str]:
        """Returns a tuple where 1st element is metadata and 2nd is url."""
        entry = self.payload["images"]["cover"]

        cover = Cover(
            self.media_id,
            0,
            self.EXTENSIONS[entry["t"]],
            (entry["w"], entry["h"]),
        )

        return (cover, cover.url)

    @property
    def thumbnail(self) -> tuple[Thumb, str]:
        """Returns a tuple where 1st element is metadata and 2nd is url."""
        entry = self.payload["images"]["thumbnail"]

        thumbnail = Thumb(
            self.media_id,
            0,
            self.EXTENSIONS[entry["t"]],
            (entry["w"], entry["h"]),
        )

        return (thumbnail, thumbnail.url)

    @property
    def media_id(self) -> int:
        """Returns the media_id of the doujin."""
        return self.payload["media_id"]

    @property
    def num_pages(self) -> int:
        """Returns the number of pages a doujin has."""
        return self.payload["num_pages"]

    @property
    def id(self) -> int:
        """Well, returns the id that was entered."""
        return self.payload["id"]

    @property
    def upload_date(self) -> dt:
        """Returns the upload date of a doujin."""
        return dt.fromtimestamp(self.payload["upload_date"], tz=timezone.utc)

    @property
    def num_favorites(self) -> int:
        """Returns the numbers of favorites a doujin has."""
        return self.payload["num_favorites"]


@dataclass(frozen=True, slots=True)
class Homepage:
    """Homepage parsing class."""

    trending_new: list[Gallery]
    new: list[Gallery]
