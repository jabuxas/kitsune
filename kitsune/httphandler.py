import ast
import asyncio
from typing import Union

import aiohttp


class HTTP:
    async def fetch(self, session: aiohttp.ClientSession, url: Union[str, int]) -> str:
        # does the get requests
        async with session.get(url) as response:
            return await response.text()

    async def html(self, session: aiohttp.ClientSession, url: Union[str, int]) -> dict:
        # formats the urls for the get requests
        url = f"https://nhentai.net/api/gallery/{url}"
        # cloudflare skip any% speedrun
        uri = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"
        # get request
        html = await self.fetch(session, uri)
        # transform the strings to dictionaries
        html = ast.literal_eval(html)
        return html

    async def main(self, urls: Union[str, list], session=None) -> Union[dict, list]:
        if session is None:
            session = aiohttp.ClientSession()

        if isinstance(urls, list):
            tasks = [self.html(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
        else:
            results = await self.html(session, urls)

        await session.close()

        return results
