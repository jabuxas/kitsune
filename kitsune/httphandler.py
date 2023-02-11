from typing import Union

import aiohttp


class HTTP:
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        # does the get requests
        async with session.get(url) as response:
            return await response.json()

    async def html(self, session: aiohttp.ClientSession, url: Union[str, int]) -> dict:
        # formats the urls for the get requests
        url = f"https://nhentai.net/api/gallery/{url}"
        # cloudflare skip any% speedrun
        uri = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"
        # get request
        return await self.fetch(session, uri)

    async def main(self, url: Union[str, int], session) -> Union[dict, list]:
        results = await self.html(session, url)
        return results
