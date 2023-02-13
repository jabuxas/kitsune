import asyncio
import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from typing import List

import aiohttp

from kitsune.gallery import Gallery
from kitsune.http import HTTP

__all__ = ("Doujin",)


class Doujin:
    def __init__(
        self,
        session=None,
        loop=None,
    ):
        self.cache: Dict[int, Gallery] = {}
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def fetch_gallery(self, __id: int, session=None) -> Gallery:
        """
        Standard fetching of the gallery, it receives as argument
        an integer, and returns a gallery object
        """
        # if gallery is in cache, use that
        if gallery := self.cache.get(__id):
            return gallery

        if session is None:
            session = self.session

        # fetch payload
        payload = await HTTP().html(session, __id)
        gallery = Gallery(payload)
        # add payload to cache
        self.cache[gallery.id] = gallery

        return gallery

    async def fetch_galleries(self, ids: list):
        """
        Receives a list of doujin's id's as argument,
        returns a list with the gallery objects of those id's
        """
        session = self.session
        tasks = (self.fetch_gallery(__id, session) for __id in ids)
        results = await asyncio.gather(*tasks)
        return results

    async def fetch_related(self, __id: int) -> List[Gallery]:
        """
        Parses all related doujin to the id specified,
        returning a list with the objects of each
        """
        session = self.session
        url = f"{__id}/related"
        payload = await HTTP().html(session, url)
        galleries = [Gallery(result) for result in payload["result"]]

        for doujin in galleries:
            self.cache[doujin.id] = doujin

        return galleries

    async def download(self, location: str, __id: int):
        """
        Download the doujin pages to the specified location.
        Accepts the absolute path as location. e.g:
            '/home/user/tmp'
        without trailing slashes.

        Accepts an int id as the __id.
        """
        count = 0
        location = f"{location}/{__id}"
        # The below just checks if the folders exists
        if not pathlib.Path(location).exists():
            pathlib.Path(location).mkdir()
        # await payload
        links = await self.fetch_gallery(__id)
        session = self.session
        with ThreadPoolExecutor() as executor:
            for link in links.pages:
                # link is a tuple with metadata and url
                link = link[1]
                count += 1
                # below checks if the files exists
                filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
                if pathlib.Path(filename).exists():
                    print(f"File {filename} already exists, skipping download.")
                    continue
                image = await HTTP().fetch(session, link, json=False)
                executor.submit(self.write_file, location, count, link, image)

    def write_file(self, location: str, count: int, link: str, image: bytes) -> None:
        filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
        with open(f"{filename}", mode="wb") as f:
            f.write(image)
