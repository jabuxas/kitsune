import ast
import asyncio

import aiohttp


class HTTP:
    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def main(self, url):
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession(loop=loop) as session:
            url = f"https://nhentai.net/api/gallery/{url}"
            uri = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"
            html = await self.fetch(session, uri)
            html = ast.literal_eval(html)
            return html


class Doujin:
    def __init__(self, url):
        self.id = url
        self.payload = asyncio.run(HTTP().main(url))

    async def tags(self):
        l = []
        for itens in self.payload["tags"]:
            l.append(itens["name"])
        return l

doujin = Doujin(123654)
asyncio.run(doujin.tags())
