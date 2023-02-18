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
        """Get requests.

        The json argument decides whether to parse the payload or receive it as bytes.
        """
        # does the get requests
        async with session.get(url) as response:
            if "application/json" in response.headers.get("Content-Type"):
                return await response.json()
            elif "text/html" in response.headers.get("Content-Type"):
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
    def write_file(location: str, count: int, link: str, image: bytes) -> None:
        """Write bytes to a file."""
        filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
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

    async def get_popular(self, session) -> set[Gallery]:
        payload = await self.gallery(session, "")
        soup = BeautifulSoup(payload, "html.parser")
        return [div.text.strip() for div in soup.find_all("div", class_="caption")][:5]
