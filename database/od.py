from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup as soup
import logging as log
import httpx
import asyncio

log.basicConfig(level=log.DEBUG)
RATE_LIMIT = 5

class OpenDirectory():
    __data = None
    __soup = None
    __folders = list()
    __files = list()
    __semaphore = asyncio.Semaphore(RATE_LIMIT)
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36" }
    extensions = ('7z', 'mp3', 'ogg', 'opus')

    def __init__(self, link:str) -> None:
        log.debug(f"Creating OpenDirectory({link})")
        self.link = link


    # Only make one http request 
    async def request(self):
        log.debug("Starting HTTP request")
        if self.__data != None:
            return self.__data
        async with httpx.AsyncClient() as client:
            self.__data = await client.get(self.link, headers=self.headers)
        if self.__data.status_code != 200:
            log.fatal(f"Couldn't retreive data: {self.__data}")
        log.debug(f"Retreived data: {self.__data}")
        return self.__data

    @property
    def soup(self):
        log.debug("Creating soup")
        if not self.__soup:
            self.__soup = soup(self.__data.text, 'html.parser')
        return self.__soup

    async def fetch(self) -> None:
        log.debug("Fetching data from soup")
        # TODO: Maybe refactor so this uses a css selector to skip those
        for f in self.soup.select("pre a"):
            if f.text in ["Name", "Last modified", "Size", "Description", "Parent Directory"]: 
                continue
            file = f.get('href')
            if not file:
                continue
            if file.endswith('/'):
                self.__folders.append(f"{self.link}{file}")
            elif file.endswith(self.extensions):
                self.__files.append(f"{self.link}{file}")
        log.debug(f"Found folders: {self.__folders}")
        log.debug(f"Found files: {self.__files}")

    
    async def download_all(self):
        await asyncio.gather(*[self.__download(file) for file in self.__files])

    async def __download(self, link:str):
        output = unquote(urlparse(link).path.split("/")[-1])
        async with self.__semaphore:
            log.debug(f"Downloading file: {link} to {output}")
            client = httpx.AsyncClient()
            async with client.stream('GET', f"{link}") as response:
                log.debug(f"Attempting to download file: {output}")
                with open(output, 'wb') as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
            await client.aclose()

async def main(): 
    link = "https://wii.joshw.info/"
    link = "https://nsf.joshw.info/0-9/"
    d = OpenDirectory(link)
    await d.request()
    await d.fetch()
    await d.download_all()

if __name__ == "__main__":
    asyncio.run(main())
