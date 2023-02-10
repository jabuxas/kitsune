import asyncio
import pathlib
from typing import Dict

import wget

from kitsune.gallery import Gallery
from kitsune.httphandler import HTTP

__all__ = ("Doujin",)


class Doujin:
    loop = asyncio.get_event_loop()

    def __init__(self, id):
        self.__id = id
        # asyncio.set_event_loop_policy(None)
        self.cache: Dict[int, Gallery] = {}

    async def fetch_gallery_data(self):
        if gallery := self.cache.get(self.__id):
            return gallery

        payload = await HTTP().jabuxas(self.__id)
        gallery = Gallery(payload)
        self.cache[gallery.id] = gallery

        return gallery

    async def download(self, location):
        count = 0
        # The below just checks if the folders exists
        p = pathlib.Path(f"{location}/{self.__id}")
        if not p.exists():
            p.mkdir()
        location = f"{location}/{self.__id}"
        links = await self.fetch_gallery_data()
        for link in links.pages:
            count += 1
            # below checks if the files exists
            filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
            if pathlib.Path(filename).exists():
                print(f"File {filename} already exists, skipping download.")
                continue
            wget.download(link, f"{location}/{str(count).zfill(4)}.{link[-3:]}")
