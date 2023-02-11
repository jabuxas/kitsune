import asyncio
import pathlib
from typing import Dict, List

import aiohttp
import wget

from kitsune.gallery import Gallery
from kitsune.httphandler import HTTP

__all__ = ("Doujin",)


class Doujin:
    def __init__(self):
        self.cache: Dict[int, Gallery] = {}

    async def fetch_gallery(
        self, __id: int, session=None, close: bool = True
    ) -> Gallery:
        """
        Standard fetching of the gallery, it receives as argument
        an integer, and returns a gallery object
        """
        # if gallery is in cache, use that
        if gallery := self.cache.get(__id):
            return gallery

        if session is None:
            session = aiohttp.ClientSession()

        # fetch payload
        payload = await HTTP().main(__id, session)
        gallery = Gallery(payload)
        # add payload to cache
        self.cache[gallery.id] = gallery

        # if calling this function without special paratemers, remember to
        # close at the end of it
        if close:
            await session.close()

        return gallery

    async def fetch_galleries(self, ids: list) -> List[Gallery]:
        """
        Receives a list of doujin's id's as argument,
        returns a list with the gallery objects of those id's
        """
        session = aiohttp.ClientSession()
        tasks = [self.fetch_gallery(__id, session, close=False) for __id in ids]
        results = await asyncio.gather(*tasks)
        await session.close()
        return results

    async def fetch_related(self, __id: int) -> List[Gallery]:
        """
        Parses all related doujin to the id specified,
        returning a list with the objects of each
        """
        session = aiohttp.ClientSession()
        url = f"{__id}/related"
        payload = await HTTP().main(url, session)
        gallery = [Gallery(result) for result in payload["result"]]

        for doujin in gallery:
            self.cache[doujin.id] = doujin

        await session.close()
        return gallery

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
