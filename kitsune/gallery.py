from dataclasses import dataclass

__all__ = (
    "Title",
    "Tag",
    "Page",
    "Cover",
    "Thumb" "Gallery",
)


@dataclass(frozen=True, slots=True)
class Title:
    english: str
    japanese: str
    pretty: str


@dataclass(frozen=True, slots=True)
class Tag:
    id: int
    type: str
    name: str
    url: str
    count: int


@dataclass(frozen=True, slots=True)
class Page:
    def __getitem__(self, key):
        return getattr(self, key)

    media_id: int
    num: int
    type: str
    resolution: tuple[int, int]

    @property
    def url(self):
        return f"https://i.nhentai.net/galleries/{self.media_id}/{self.num}.{self.type}"


class Cover(Page):
    @property
    def url(self):
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover.{self.type}"


class Thumb(Page):
    @property
    def url(self):
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{self.type}"


class Gallery:
    EXTENSIONS = {"j": "jpg", "p": "png", "g": "gif"}

    def __init__(self, payload):
        self.payload = payload

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def tags(self) -> list[Tag]:
        """
        Returns a list with metadata of all the tags
        of the doujin specified.
        """

        return [Tag(*tag.values()) for tag in self.payload["tags"]]

    @property
    def title(self) -> Title:
        """
        Returns the title in English,
        Japanese or Pretty, though it might not
        have the latter two.
        """

        return Title(*(self.payload["title"].values()))

    @property
    def pages(self) -> list[Page]:
        """
        Returns a list of tuples, where 1st element
        of the tuple is metadata, and 2nd is the url
        """

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
        """
        Returns a tuple where 1st element is metadata
        and 2nd is url
        """

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
        """
        Returns a tuple where 1st element is metadata
        and 2nd is url
        """

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
        """
        Returns the media_id of the doujin
        """

        return self.payload["media_id"]

    @property
    def num_pages(self) -> int:
        """
        Returns the number of pages a doujin has
        """

        return self.payload["num_pages"]

    @property
    def id(self) -> int:
        """
        Well, returns the id that was entered

        """
        return self.payload["id"]
