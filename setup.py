from setuptools import find_packages
from setuptools import setup

VERSION="0.1"

setup(
    name="kitsune-nh",
    version=VERSION,
    author="https://github.com/SeedOfLight",
    author_email="<lucasbarbieri.c@gmail.com>",
    license="BSD3",
    description="async nhentai wrapper",
    # long_description_content_type="text/markdown",
    # long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["aiohttp"],
    keywords=["python", "wrapper", "scraper", "nhentai", "anime", "manga"]
    )

