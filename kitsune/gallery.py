import pathlib

import wget


class Gallery:
    EXTENSIONS = {"j": "jpg", "p": "png", "g": "gif"}

    def __init__(self, payload):
        self.payload = payload

    def tags(self):
        return [items["name"] for items in self.payload["tags"]]

    def media_id(self):
        return self.payload["media_id"]

    def fetch_cover(self):
        __type = self.payload["images"]["cover"]["t"]
        return f"https://t.nhentai.net/galleries/{self.media_id()}/cover.{self.EXTENSIONS[__type]}"

    def fetch_thumb(self):
        media_id = self.media_id()
        extension = self.payload["images"]["thumbnail"]["t"]
        return f"https://t.nhentai.net/galleries/{media_id}/thumb.{self.EXTENSIONS[extension]}"

    def fetch_related(self):
        return f"https://nhentai.net/api/gallery/{self.id_doujin()}/related"

    def len_doujin(self):
        return len(self.payload["images"]["pages"])

    def fetch_name_english(self):
        doujin_name = self.payload["title"]["english"]
        return doujin_name

    def fetch_name_japanese(self):
        doujin_name = self.payload["title"]["japanese"]
        return doujin_name

    def fetch_name_pretty(self):
        doujin_name = self.payload["title"]["pretty"]
        return doujin_name
    
    def doujin_type(self,loc):
        __type = self.payload["images"]["pages"][loc]["t"]
        extension = self.EXTENSIONS[__type]
        return extension

    def id_doujin(self):
        return self.payload("id")

    def image_urls(self):
        l = []
        for num in range(self.len_doujin()):
            extension = self.doujin_type(num)
            num += 1
            image = f"https://i.nhentai.net/galleries/{self.media_id()}/{num}.{extension}"
            l.append(image)
        return l

    def download_url(self, location):
        count = 0
        # The below just checks if the folders exists
        if location[-1] == "/":
            location = location.rstrip("/")
        p = pathlib.Path(f"{location}/{self.fetch_name_english()}")
        if not p.exists():
            p.mkdir()
        location = f"{location}/{self.fetch_name_english()}"
        for link in self.image_urls():
            count += 1
            # below checks if the files exists
            if not pathlib.Path(
                f"{location}/{str(count).zfill(4)}{link[-3:]}"
            ).exists():
                wget.download(link, f"{location}/{str(count).zfill(4)}.{link[-3:]}")
