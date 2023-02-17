from typing import Optional, Union

import aiohttp


class HTTP:
    async def fetch(
        self, session: aiohttp.ClientSession, url: str, json: Optional[bool] = True
    ):
        # does the get requests
        async with session.get(url) as response:
            if json:
                return await response.json()
            else:
                return await response.read()

    async def gallery(
        self, session: aiohttp.ClientSession, __id: Union[int, str]
    ) -> dict:
        # formats the urls for the get requests
        url = f"https://nhentai.net/api/gallery/{__id}"
        url = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"

        # get request
        return await self.fetch(session, url)

    def write_file(self, location: str, count: int, link: str, image: bytes) -> None:
        filename = f"{location}/{str(count).zfill(4)}.{link[-3:]}"
        with open(f"{filename}", mode="wb") as f:
            f.write(image)

    async def google(self, session, url) -> dict:
        # cloudflare skip any% speedrun
        main = f"https://nhentai-net.translate.goog/{url}&_x_tr_sl=vi&_x_tr_tl=en&_x_tr_hl=vi&_x_tr_pto=wapp"
        return await self.fetch(session, main)
