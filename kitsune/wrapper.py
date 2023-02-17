import asyncio
import pathlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt
from datetime import timezone
from typing import Dict
from typing import List

import aiohttp
from tqdm import tqdm

from kitsune.gallery import Comment
from kitsune.gallery import Gallery
from kitsune.gallery import User
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
        payload = await HTTP().gallery(session, __id)
        gallery = Gallery(payload)
        # add payload to cache
        self.cache[gallery.id] = gallery

        return gallery

    async def fetch_galleries(self, ids: list) -> list[Gallery]:
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
        payload = await HTTP().gallery(session, url)
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
            for link in tqdm(links.pages, desc="Downloading", ascii=True):
                # link is a tuple with metadata and url
                link = link[1]
                count += 1
                # below checks if the files exists
                filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
                if pathlib.Path(filename).exists():
                    print(f"File {filename} already exists, skipping download.")
                    continue
                image = await HTTP().fetch(session, link, json=False)
                executor.submit(HTTP().write_file, location, count, link, image)

    async def comments(self, __id) -> list[Comment]:
        """
        Retrieves the comments from a Doujin and their
        metadata, such as their id, user picture url, etc.
        """
        session = self.session
        url = f"{__id}/comments"
        payload = await HTTP().gallery(session, url)
        comments = [
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
        return comments

    async def search_query(
        self, query: str, page: int = 1, sort: str = "popular"
    ) -> list[Gallery]:
        """
        Searches by query, defaults to page 1 and popular sorting.

        Let's say you want to search for doujins that have the
        ahegao tag, on page 3, sorting by week popular.

        You can do:

        async def main()
            async with kitsune.Doujin() as doujin:
                search = await doujin.search_query("tag:ahegao", 3, "popular-week")
                print(search)

        asyncio.run(main())

        Sorting accepts:
            popular
            popular-month
            popular-week
            popular-day
            date

        Some tags don't have certain sortings, for example ahegao doesn't seem
        to have 'date' nor 'popular-day' when searching via tag name on page 1, but yaoi
        on the other hand has both.
        Traceback "KeyError: 'result'" means it doesn't have that sorting.
        """
        session = self.session
        params = {"query": {query}, "page": page, "sort": sort}
        base_url = f"api/galleries/search"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        payload = await HTTP().google(session, url)
        payload = payload["result"]
        return [Gallery(data) for data in payload]

    async def search_tags(
        self, tag_id: int, page: int = 1, sort: str = "popular"
    ) -> list[Gallery]:
        """
        Searches by tag, defaults to page 1 and popular sorting.

        Let's say you want to search for doujins that have the
        ahegao tag (id 13989), on page 1, sorting by month popular.

        You can do:

        async def main()
            async with kitsune.Doujin() as doujin:
                search = await doujin.search_tags(query=13989, sort="popular-month")
                print(search)

        asyncio.run(main())

        Sorting accepts:
            popular
            popular-month
            popular-week
            popular-day (technically, but I haven't found any doujin that has this)
            date

        Some tags have weird behaviour, for example ahegao doesn't seem
        to have 'date' when searching via tag name, but with tag_id on the other hand it does.
        Traceback "KeyError: 'result'" means it doesn't have that sorting.
        """
        session = self.session
        params = {"tag_id": tag_id, "page": page, "sort": sort}
        base_url = f"api/galleries/tagged"
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        payload = await HTTP().google(session, url)
        payload = payload["result"]
        return [Gallery(data) for data in payload]
