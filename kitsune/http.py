import json
from typing import Union

import aiohttp
from bs4 import BeautifulSoup

from kitsune.gallery import Gallery


class HTTP:
    """Main fetching class."""

    async def fetch(
        self, session: aiohttp.ClientSession, url: str
    ) -> Union[dict, bytes, str]:
        """GET requests."""
        # does the get requests
        async with session.get(url) as response:
            if response.status == 429:
                return "rate limited :)"
            content_type = response.headers["Content-Type"]
            if content_type == "application/json":
                return await response.json()
            elif content_type == "text/html":
                return await response.text()
            else:
                return await response.read()

    async def gallery(self, session: aiohttp.ClientSession, url: str) -> dict:
        """Class method used by normal requests that aren't queries."""
        # formats the urls for the get requests
        url = f"https://nhentai.net/{url}"
        url = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"

        # get request
        return await self.fetch(session, url)

    @staticmethod
    def write_file(filename: str, image: bytes) -> None:
        """Write bytes to a file."""
        with open(f"{filename}", mode="wb") as f:
            f.write(image)

    async def google(self, session, url) -> dict:
        """Class method used by queries."""
        # cloudflare skip any% speedrun
        main = f"https://nhentai-net.translate.goog/{url}&_x_tr_sl=vi&_x_tr_tl=en&_x_tr_hl=vi&_x_tr_pto=wapp"
        return await self.fetch(session, main)

    @staticmethod
    def write_json(payload: dict) -> None:
        """Write the json payload to local directory as __id.json."""
        with open(f"{payload['id']}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2))

    async def get_popular(self, session) -> list[Gallery]:
        payload = await self.gallery(session, "")
        soup = BeautifulSoup(payload, "html.parser")
        return [div.text.strip() for div in soup.find_all("div", class_="caption")][:5]
