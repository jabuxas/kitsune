import asyncio

from kitsune.gallery import Gallery
from kitsune.httphandler import HTTP

__all__ = ("Doujin",)

class Doujin:
    def __init__(self, id):
        self.__id = id
        # asyncio.set_event_loop_policy(None)
        loop = asyncio.get_event_loop()
        self.payload = loop.run_until_complete(
            asyncio.ensure_future(HTTP().jabuxas(self.__id))
        )

    @property
    def fetch_tags(self):
        return Gallery(self.payload).tags()
    
    @property
    def t_english(self):
        return Gallery(self.payload).fetch_name_english()

    @property
    def t_pretty(self):
        return Gallery(self.payload).fetch_name_pretty()

    @property
    def t_japanese(self):
        return Gallery(self.payload).fetch_name_japanese()

    @property
    def fetch_cover(self):
        return Gallery(self.payload).fetch_cover()

    @property
    def fetch_thumb(self):
        return Gallery(self.payload).fetch_thumb()

    @property
    def fetch_related(self):
        return Gallery(self.__id).fetch_related()

    @property
    def fetch_pages(self):
        """
        Returns the url's of the doujin's images.
        """
        return Gallery(self.payload).image_urls()

    def download_pages(self, location):
        """
        Downloads the pages of a certain Doujin

        Accepts 1 argument -> location
        pass it as '/home/user/Documents'
        """
        return Gallery(self.payload).download_url(location)
