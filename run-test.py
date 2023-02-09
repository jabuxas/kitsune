import kitsune
import sys
import os

tmp = os.getcwd()
doujin = kitsune.Doujin(123456)

doujin.download_pages(f'{tmp}/testtest')
#ab
