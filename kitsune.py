import ast
import asyncio
import wget
import aiohttp
import os
import sys




class Doujin:
    def __init__(self, url):
        self.__id = url
        loop = asyncio.get_event_loop()
        self.payload = loop.run_until_complete(asyncio.ensure_future(self.main(self.__id)))

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def main(self, url):
        async with aiohttp.ClientSession() as session:
            url = f"https://nhentai.net/api/gallery/{url}"
            uri = f"https://translate.google.com/translate?sl=vi&tl=en&hl=vi&u={url}&client=webapp"
            html = await self.fetch(session, uri)
            html = ast.literal_eval(html)
            return html

    def fetch_tags(self):
        return Tag(self.payload).tags()

    def fetch_cover(self):
        return Cover(self.payload).fetch_cover()

    def fetch_thumb(self):
        return Thumb(self.payload).fetch_thumb()

    def fetch_related(self):
        return Related(self.__id).fetch_related()

    def fetch_pages(self):
        return Page(self.payload).image_urls()

    def download_pages(self):
        return Page(self.payload).download_url()

class Tag:
    def __init__(self, payload):
        self.payload = payload

    def tags(self):
        l = []
        for items in self.payload["tags"]:
            l.append(items["name"])
        return l


class Cover:
    def __init__(self, payload):
        self.payload = payload

    def fetch_mid(self):
        return self.payload["media_id"]

    def fetch_exten(self):
        __type = self.payload["images"]["cover"]["t"]
        return Conversion().convertor(__type)

    def fetch_cover(self):
        media_id = self.fetch_mid()
        extension = self.fetch_exten()
        return f"https://t.nhentai.net/galleries/{media_id}/cover.{extension}"



class Thumb:
    def __init__(self, payload):
        self.payload = payload

    def fetch_mid(self):
        return self.payload["media_id"]

    def fetch_exten(self):
        __type = self.payload["images"]["thumbnail"]["t"]
        return Conversion().convertor(__type)

    def fetch_thumb(self):
        media_id = self.fetch_mid()
        extension = self.fetch_exten()
        return f"https://t.nhentai.net/galleries/{media_id}/thumb.{extension}"


class Conversion:
    def convertor(self, payload):
        if payload == "j":
            return "jpg"
        elif payload == "g":
            return "gif"
        else:
            return "png"


class Related:
    def __init__(self, __id):
        self.__id = __id

    def fetch_related(self):
        return f"https://nhentai.net/api/gallery/{self.__id}/related"

class Page:
    def __init__(self, payload):
        self.payload = payload

    def len_doujin(self):
        __len = len(self.payload["images"]["pages"])
        return __len

    def type_doujin(self):
        __type =  self.payload["images"]["pages"][0]["t"]
        extension = Conversion().convertor(__type)
        return extension

    def fetch_mid(self):
        return self.payload["media_id"]

    def image_urls(self):
        l = []
        for num in range(self.len_doujin()):
            num += 1
            image = f"https://i.nhentai.net/galleries/{self.fetch_mid()}/{num}.{self.type_doujin()}"
            l.append(image)
        return l
    
    def download_url(self):
        count = 0
        cur_wd = os.getcwd()
        for link in self.image_urls():
            count +=1
            #wget.download(link, f'/home/jab/tmp/{self.fetch_mid()}-{count}.jpg')
            wget.download(link , f'{cur_wd}/tmp/{self.fetch_mid()}-{count.zfill(3)}.jpg')
            #I added it so it will add them to the working direcotry. 


#doujin = Doujin(123654)
input_doujin = sys.argv[1]
if input_doujin and int(input_doujin) > 0:
    doujin = Doujin(input_doujin)
else:
    print("Please enter a manga numbers from nhentia")
print(doujin.download_pages())
# Add the above to accept an input and check for it it is not empty

# print(doujin.fetch_thumb())
# print(doujin.fetch_related())
