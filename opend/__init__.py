from opend.file import File
from typing import List
from utils import unq
from bs4 import BeautifulSoup as soup
import logging as log
import httpx
import asyncio


class OpenDirectory:
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36" }
    extensions = ('7z', 'mp3', 'ogg', 'opus')


    def __init__(self, link:str, limit=10) -> None:
        self.link = link
        self.__semaphore = asyncio.Semaphore(limit)
        self.__data: httpx.Response = None # pyright: ignore
        self.__soup: soup = None # pyright: ignore
        self.__folders: List['OpenDirectory'] = list()
        self.__files: List[File] = list()


    def __str__(self) -> str:
        return self.link


    async def request(self):
        """
        This method sends the http request
        """
        log.debug(f"Sending HTTP request to {self}")
        # Retreive cached http request if present
        if self.__data != None:
            return self.__data
        # Asynchronously make a request
        async with self.__semaphore:
            async with httpx.AsyncClient() as client:
                self.__data = await client.get(self.link, headers=self.headers)
            if self.__data.status_code != 200:
                log.fatal(f"Couldn't retreive data: {self.__data}")
        return self.__data


    async def soup(self):
        """
        This method returns the html parser. It calls the request function
        """
        r = await self.request()
        if not self.__soup:
            self.__soup = soup(unq(r.text), 'html.parser')
        return self.__soup


    async def fetch(self):
        """
        This method scrapes the http request for hyperlinks
            It will either use the cached http request or call the http request
        """
        soup = await self.soup()
        for f in soup.select("pre a"):
            # These are top header fields
            if f.text in ["Name", "Last modified", "Size", "Description", "Parent Directory"]: 
                continue

            file = f.get('href')
            # Null guard
            if not file:
                continue

            # If the file is a directory
            if file.endswith('/'): # pyright: ignore 
                self.__folders.append(OpenDirectory(f"{self.link}{file}"))
            # If this is a file
            elif file.endswith(self.extensions): # pyright: ignore 
                self.__files.append(File(f"{self.link}{file}"))
        log.debug(f"Found folders: {self.__folders}")
        log.debug(f"Found files: {self.__files}")


    async def download_tasks(self):
        """
        Returns a list of the desired tasks
        """
        await self.fetch()
        tasks = [d.fetch() for d in self.__folders]
        return tasks


    async def files(self):
        """
        Returns a list containing all the urls to all files
        """
        await self.fetch()
        files = list(self.__files)

        tasks = [d.request() for d in self.__folders]
        await asyncio.gather(*tasks)

        tasks = [d.fetch() for d in self.__folders]
        await asyncio.gather(*tasks)

        for d in self.__folders:
            files += d.__files

        return files


async def main(): 
    #link = "https://wii.joshw.info/"
    #link = "https://nsf.joshw.info/0-9/"
    link = "https://nsf.joshw.info/"
    d = OpenDirectory(link)
    await d.fetch()
    #await d.download_files()
    #await d.download_folders()

if __name__ == "__main__":
    asyncio.run(main())
