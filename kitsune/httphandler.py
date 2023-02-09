import ast

import aiohttp


class HTTP:
    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def jabuxas(self, url):
        async with aiohttp.ClientSession() as session:
            url = f"https://nhentai.net/api/gallery/{url}"
            uri = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"
            html = await self.fetch(session, uri)
            html = ast.literal_eval(html)
            return html
