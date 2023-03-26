from urllib.parse import urlparse, unquote
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

    
    async def request(self):
        """
        This method sends the http request
        """
        log.debug("Starting HTTP request")
        # Retreive cached http request if present
        if self.__data != None:
            return self.__data
        # Asynchronously make a request
        async with httpx.AsyncClient() as client:
            self.__data = await client.get(self.link, headers=self.headers)
        if self.__data.status_code != 200:
            log.fatal(f"Couldn't retreive data: {self.__data}")
        log.debug(f"Retreived data: {self.__data}")
        return self.__data


    async def soup(self):
        """
        This method returns the html parser. It calls the request function
        """
        log.debug("Creating soup")
        r = await self.request()
        if not self.__soup:
            self.__soup = soup(r.text, 'html.parser')
        return self.__soup


    async def fetch(self) -> None:
        log.debug("Fetching data from soup")
        # TODO: Maybe refactor so this uses a css selector to skip those
        soup = await self.soup()
        for f in soup.select("pre a"):
            # These are top header fields
            if f.text in ["Name", "Last modified", "Size", "Description", "Parent Directory"]: 
                continue
            # Header field
            file = f.get('href')
            # Null guard
            if not file:
                continue
            # If the file is a directory
            if file.endswith('/'):
                self.__folders.append(f"{self.link}{file}")
            # If this is a file
            elif file.endswith(self.extensions):
                self.__files.append(f"{self.link}{file}")
        log.debug(f"Found folders: {self.__folders}")
        log.debug(f"Found files: {self.__files}")

    
    async def download_file(self, link:str):
        # This gets the basename of the link
        output = unquote(urlparse(link).path.split("/")[-1])
        # Semaphores ensure the jobs do not exceed the size specified by the semaphore
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


    async def download_folder(self, d):
        """
        Downloads a folder
        """
        if not isinstance(d, OpenDirectory):
            return
        await d.fetch()
        tasks = [d.download_files()]
        tasks += [d.__download_folder(folder, tasks) for folder in d.__folders] 
        await asyncio.gather(*tasks)


    async def __download_folder(self, d, tasks):
        """
        A helper method that creates tasks for subdirectories
        """
        if not isinstance(d, OpenDirectory):
            return
        await d.fetch()
        tasks += [d.__download_folder(folder, tasks) for folder in d.__folders]
        return tasks


async def main(): 
    link = "https://wii.joshw.info/"
    link = "https://nsf.joshw.info/0-9/"
    d = OpenDirectory(link)
    await d.fetch()
    await d.download_files()

if __name__ == "__main__":
    asyncio.run(main())
