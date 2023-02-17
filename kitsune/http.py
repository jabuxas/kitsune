import json
from typing import Optional, Union

import aiohttp


class HTTP:
    """Main GET'ing class."""

    async def fetch(

        self, session: aiohttp.ClientSession, url: str, json: Optional[bool] = True
    ) -> Union[dict, bytes]:
        """Get requests.

        The json argument decides whether to parse the payload or receive it as bytes.
        """
        # does the get requests
        async with session.get(url) as response:
            if json:
                return await response.json()
            else:
                return await response.read()

    async def gallery(
        self, session: aiohttp.ClientSession, __id: Union[int, str]
    ) -> dict:
        """Class method used by normal requests that aren't queries."""
        # formats the urls for the get requests
        url = f"https://nhentai.net/api/gallery/{__id}"
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
