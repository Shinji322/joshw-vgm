from typing import List
from utils import basename, unq
from bs4 import BeautifulSoup as soup
import logging as log
import httpx
import asyncio

try:
    from alive_progress import alive_bar
    hasbar=True
except ImportError:
    hasbar=False


log.basicConfig(level=log.DEBUG)


class OpenDirectory():
    __data: httpx.Response = None # pyright: ignore
    __soup: soup = None # pyright: ignore
    __folders: List['OpenDirectory']
    __files: List[str]
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36" }
    extensions = ('7z', 'mp3', 'ogg', 'opus')


    def __init__(self, link:str, RATE_LIMIT=10) -> None:
        self.link = link
        self.__semaphore = asyncio.Semaphore(RATE_LIMIT)
        self.__folders = list()
        self.__files = list()


    def has_folders(self) -> bool:
        for _ in self.__folders:
            return True
        return False

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
        This method fetches metadata from the current folder
        """
        log.debug("Fetching data from soup")
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
            if file.endswith('/'):
                self.__folders.append(OpenDirectory(f"{self.link}{file}"))
            # If this is a file
            elif file.endswith(self.extensions):
                self.__files.append(f"{self.link}{file}")
        log.debug(f"Found folders: {self.__folders}")
        log.debug(f"Found files: {self.__files}")

    
    async def download_file(self, link:str):
        output = basename(link)
        async with self.__semaphore:
            log.debug(f"Downloading file: {link} to {output}")
            client = httpx.AsyncClient()
            async with client.stream('GET', f"{link}") as response:
                log.debug(f"Attempting to download file: {output}")
                size = int(response.headers.get("Content-Length"))
                # This is the ~magic~!
                if hasbar:
                    with open(output, 'wb') as f, alive_bar(size) as bar:
                        async for chunk in response.aiter_bytes():
                            bar(f.write(chunk))
                else:
                    with open(output, 'wb') as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                log.debug(f"Finished downloading file {output}")
            await client.aclose()


    async def download_files(self):
        """
        Downloads all files in given directory's folder
        """
        # Queue up some tasks for everything
        await asyncio.gather(*[self.download_file(file) for file in self.__files])


    async def download_folder(self):
        """
        Downloads an entire folder
        """
        log.debug(f"Beginning download of folder: {self.link}")
        await self.fetch()
        tasks = [self.download_file(file) for file in self.__files]
        try:
            # I need to do some sort of asynchronous recursion here that i'm not smart enough to do right now
            for folder in self.__folders:
                tasks += [folder.download_file(f) for f in folder.__files]
                tasks += [folder.queue(f) for f in folder.__folders]
            # while f has folders, add their download files tasks to the task queue
        except IndexError:
            pass
        log.debug(f"Tasks: {tasks}")
        await asyncio.gather(*tasks)


    async def __download_folder(self, d: 'OpenDirectory', tasks):
        """
        A helper method that creates tasks for subdirectories
        """
        await d.fetch()
        tasks += [d.__download_folder(folder, tasks) for folder in d.__folders]
        return tasks

    def get_files(self):
        return self.__files


    async def get_all_files(self):
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
