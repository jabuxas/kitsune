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
        self.cache: Dict[int, Gallery] = {}

    async def fetch_gallery_data(self):
        # if gallery is in cache, use that
        if gallery := self.cache.get(self.__id):
            return gallery

        # fetch payload
        payload = await HTTP().jabuxas(self.__id)
        gallery = Gallery(payload)
        # add payload to cache
        self.cache[gallery.id] = gallery

        return gallery

    async def download(self, location):
        count = 0
        location = f"{location}/{self.__id}"
        # The below just checks if the folders exists
        if not pathlib.Path(location).exists():
            pathlib.Path(location).mkdir()
        # await payload
        links = await self.fetch_gallery_data()
        for link in links.pages:
            # link is a tuple with metadata and url
            link = link[1]
            count += 1
            # below checks if the files exists
            filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
            if pathlib.Path(filename).exists():
                print(f"File {filename} already exists, skipping download.")
                continue
            wget.download(link, f"{location}/{str(count).zfill(4)}.{link[-3:]}")
