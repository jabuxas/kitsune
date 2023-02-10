from dataclasses import dataclass


class Gallery:
    EXTENSIONS = {"j": "jpg", "p": "png", "g": "gif"}

    def __init__(self, payload):
        self.payload = payload

        self.pages = [
            Page(
                self.media_id,
                i + 1,
                self.EXTENSIONS[self.payload["images"]["pages"][i]["t"]],
            ).url()
            for i in range(self.num_pages)
        ]
        self.cover = Cover(
            self.EXTENSIONS[self.payload["images"]["cover"]["t"]],
            self.payload["images"]["cover"]["w"],
            self.payload["images"]["cover"]["h"],
            self.cover_url,
        )
        self.tags = [Tag(*tag.values()) for tag in self.payload["tags"]]
        self.title = Title(*(self.payload["title"].values()))
        self.thumb = Thumb(
            self.EXTENSIONS[self.payload["images"]["thumbnail"]["t"]],
            self.payload["images"]["thumbnail"]["w"],
            self.payload["images"]["thumbnail"]["h"],
            self.thumb_url,
        )

    @property
    def cover_url(self):
        __type = self.EXTENSIONS[self.payload["images"]["cover"]["t"]]
        return f"https://t.nhentai.net/galleries/{self.media_id}/cover.{__type}"

    @property
    def media_id(self):
        return self.payload["media_id"]

    @property
    def thumb_url(self):
        __type = self.EXTENSIONS[self.payload["images"]["cover"]["t"]]
        return f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{__type}"

    def fetch_related(self):
        return f"https://nhentai.net/api/gallery/{self.id}/related"

    @property
    def num_pages(self):
        return self.payload["num_pages"]

    @property
    def id(self) -> int:
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
    type: str
    width: int
    height: int
    url: str


@dataclass(frozen=True)
class Thumb:
    type: str
    width: int
    height: int
    url: str


@dataclass(frozen=True)
class Page:
    media_id: int
    num: int
    type: str

    def url(self):
        return f"https://i.nhentai.net/galleries/{self.media_id}/{self.num}.{self.type}"
