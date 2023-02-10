from dataclasses import dataclass


class Gallery:
    EXTENSIONS = {"j": "jpg", "p": "png", "g": "gif"}

    def __init__(self, payload):
        self.payload = payload

    @property
    def tags(self) -> list:
        """
        Returns a list with metadata of all the tags
        of the doujin specified.
        """
        return [Tag(*tag.values()) for tag in self.payload["tags"]]

    @property
    def title(self):
        """
        Returns the title in English,
        Japanese or Pretty, though it might not
        have the latter two.
        """
        return Title(*(self.payload["title"].values()))

    @property
    def pages(self) -> list:
        """
        Returns a list of tuples, where 1st element
        of the tuple is metadata, and 2nd is the url
        """
        pages = []
        for i in range(self.num_pages):
            page = Page(
                self.media_id,
                i + 1,
                self.EXTENSIONS[self.payload["images"]["pages"][i]["t"]],
            )
            url = page.create()
            pages.append((page, url))
        return pages

    @property
    def cover(self) -> tuple:
        """
        Returns a tuple where 1st element is metadata
        and 2nd is url
        """
        cover = Cover(
            self.media_id,
            self.EXTENSIONS[self.payload["images"]["cover"]["t"]],
            self.payload["images"]["cover"]["w"],
            self.payload["images"]["cover"]["h"],
        )
        url = cover.create()
        return (cover, url)

    @property
    def thumbnail(self) -> tuple:
        """
        Returns a tuple where 1st element is metadata
        and 2nd is url
        """
        thumbnail = Thumb(
            self.media_id,
            self.EXTENSIONS[self.payload["images"]["thumbnail"]["t"]],
            self.payload["images"]["thumbnail"]["w"],
            self.payload["images"]["thumbnail"]["h"],
        )
        url = thumbnail.create()
        return (thumbnail, url)

    @property
    def media_id(self) -> int:
        """
        Returns the media_id of the doujin
        """
        return self.payload["media_id"]

    def fetch_related(self):
        """
        Unimplemented for now.
        """
        return f"https://nhentai.net/api/gallery/{self.id}/related"

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


@dataclass(frozen=True)
class Title:
    english: str
    japanese: str
    pretty: str


@dataclass(frozen=True)
class Tag:
    id: int
    type: str
    name: str
    url: str
    count: int


@dataclass(frozen=True)
class Cover:
    media_id: int
    type: str
    width: int
    height: int

    def create(self):
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover.{self.type}"


@dataclass(frozen=True)
class Thumb:
    media_id: int
    type: str
    width: int
    height: int

    def create(self):
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{self.type}"


@dataclass(frozen=True)
class Page:
    media_id: int
    num: int
    type: str

    def create(self):
        return f"https://i.nhentai.net/galleries/{self.media_id}/{self.num}.{self.type}"
