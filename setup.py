from setuptools import find_packages
from setuptools import setup

VERSION="0.1"

setup(
    name="kitsune-nh",
    version=VERSION,
    author="https://github.com/Acertig",
    author_email="<acertig04@gmail.com>",
    license_files=("LICENSE.txt",),
    description="async nhentai wrapper",
    # long_description_content_type="text/markdown",
    # long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["aiohttp"],
    keywords=["python", "wrapper", "scraper", "nhentai", "anime", "manga"]
    )

