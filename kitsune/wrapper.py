import asyncio
import pathlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt
from datetime import timezone
from typing import Optional

import aiohttp

from kitsune.external import *
from kitsune.gallery import *
from kitsune.http import HTTP


class Doujin:
    """
    Main wrapper class.

    Accepts passing of your own ClientSession and your own Event Loop.
    """

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """Init method of the main class."""
        self.cache: dict[int, Gallery] = {}
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)

    async def __aenter__(self):
        """Async context manager enter method."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit method."""
        await self.session.close()

    async def fetch_gallery(self, __id: int, write=False) -> Gallery:
        """
        Receives as argument an integer, and returns a gallery object.

        Pass write=True flag to the function and it'll save the json payload to current directory.
        """
        # if gallery is in cache, use that
        if gallery := self.cache.get(__id):
            return gallery

        session = self.session

        # fetch payload
        url = f"api/gallery/{__id}"
        payload = await HTTP().gallery(session, url)

        if write:
            HTTP.write_json(payload)

        gallery = Gallery(payload)
        # add payload to cache
        self.cache[gallery.id] = gallery

        return gallery

    async def fetch_galleries(self, ids: list[int]) -> list[Gallery]:
        """
        Retrieve multiple galleries at the same time.

        Accepts a list of int ids of doujins.
        """
        tasks = (self.fetch_gallery(__id) for __id in ids)
        return await asyncio.gather(*tasks)

    async def fetch_related(self, __id: int) -> list[Gallery]:
        """
        Parse all related doujin to the id specified.

        Returns a list with Gallery objects.
        """
        session = self.session
        url = f"api/gallery/{__id}/related"
        payload = await HTTP().gallery(session, url)
        galleries = [Gallery(result) for result in payload["result"]]

        for doujin in galleries:
            self.cache[doujin.id] = doujin

        return galleries

    async def download(self, location: str, __id: int) -> None:
        """
        Download the doujin pages to the specified location.

        Accepts the absolute path as location without trailing slashes.

        Accepts doujin id as int.
        """
        location = f"{location}/{__id}"
        # The below just checks if the folders exists
        if not pathlib.Path(location).exists():
            pathlib.Path(location).mkdir()
        # await payload
        gallery = await self.fetch_gallery(__id)
        session = self.session
        tasks = []
        with ThreadPoolExecutor() as executor:
            for pages, link in gallery.pages:
                ext = pages.extension_type
                num = pages.page_num
                # below checks if the files exists
                filename = f"{location}/{str(num).zfill(4)}.{ext}"
                if pathlib.Path(filename).exists():
                    print(f"File {filename} already exists, skipping download.")
                    continue
                task = asyncio.create_task(HTTP.fetch(session, link))
                tasks.append((task, filename))

            for task, loc in tasks:
                image = await task
                executor.submit(HTTP.write_file, loc, image)

    async def download_multiple(self, location: str, ids: list[int]) -> list[None]:
        """
        Download multiple doujins.

        Accepts absolute path as location without trailing slashes.

        Accepts an integer list with the ids of the doujins to be downloaded.
        """
        tasks = [asyncio.create_task(self.download(location, i)) for i in ids]
        return await asyncio.gather(*tasks)

    async def comments(self, __id) -> list[Comment]:
        """
        Retrieve the comments from a Doujin and their metadata.

        Metadata such as time of posting, id, user stats, user image url
        """
        session = self.session
        url = f"api/gallery/{__id}/comments"
        payload = await HTTP().gallery(session, url)
        return [
            Comment(
                data["id"],
                data["gallery_id"],
                User(
                    data["poster"]["id"],
                    data["poster"]["username"],
                    data["poster"]["slug"],
                    f'https://i.nhentai.net/{data["poster"]["avatar_url"]}',
                    data["poster"]["is_superuser"],
                    data["poster"]["is_staff"],
                ),
                dt.fromtimestamp(data["post_date"], tz=timezone.utc),
                data["body"],
            )
            for data in payload
        ]

    async def search_query(
        self, query: str, page: int = 1, sort: Sort = Sort.POPULAR
    ) -> list[Gallery]:
        """
        Search by query, defaults to page 1 and popular sorting.

        Sorting accepts all enums from Sort class.
        """
        session = self.session
        params = {"query": {query}, "page": page, "sort": sort}
        base_url = f"api/galleries/search"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        payload = await HTTP().google(session, url)
        payload = payload["result"]
        return [Gallery(data) for data in payload]

    async def search_tags(
        self, tag_id: int, page: int = 1, sort: Sort = Sort.POPULAR
    ) -> list[Gallery]:
        """
        Search by tag, defaults to page 1 and popular sorting.

        Sorting accepts all enums from Sort class.
        """
        session = self.session
        params = {"tag_id": tag_id, "page": page, "sort": sort}
        base_url = f"api/galleries/tagged"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        payload = await HTTP().google(session, url)
        payload = payload["result"]
        return [Gallery(data) for data in payload]

    async def get_homepage(self) -> Homepage:
        """
        Fetch the nhentai homepage for the day.

        Retrieves a total of 30 doujins, being 5 the "Trending" and the other 25 new releases.
        """
        session = self.session
        doujins = await self.search_query(query="*", sort=Sort.POPULAR_TODAY)
        titles = await HTTP().get_popular(session)
        popular = [doujin for doujin in doujins if doujin.title.english in titles]
        homepage = "api/galleries/all?page=1"
        homepage_fetch = await HTTP().gallery(session, homepage)
        home = [Gallery(data) for data in homepage_fetch["result"]]
        return Homepage(popular, home)
