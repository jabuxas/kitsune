from typing import Union, Optional

import aiohttp

class HTTP:
    async def fetch(self, session: aiohttp.ClientSession, url: str, json: Optional[bool] = True):
        # does the get requests
        async with session.get(url) as response:
            if json:
                return await response.json()
            else:
                return await response.read()

    async def html(self, session: aiohttp.ClientSession, url: Union[int, str]) -> dict:
        # formats the urls for the get requests
        url = f"https://nhentai.net/api/gallery/{url}"
        # cloudflare skip any% speedrun
        uri = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"
        # get request
        return await self.fetch(session, uri)
