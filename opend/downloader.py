from typing import Iterable
from opend import OpenDirectory
from opend.file import File
import asyncio
import httpx
import logging as log
try:
    from alive_progress import alive_bar
    hasbar=True
except ImportError:
    hasbar=False


class Downloader:
    __semaphore: asyncio.Semaphore = None # pyright: ignore 
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36" }

    def __init__(self, limit=10) -> None:
        self.__semaphore = asyncio.Semaphore(limit)


    async def file(self, file: File, output: str=None): # pyright: ignore 
        if output is None:
            output = file.basename
        async with self.__semaphore:
            client = httpx.AsyncClient()
            async with client.stream('GET', f"{file}") as response:
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


    async def files(self, links:Iterable[File]):
        await asyncio.gather(*[self.file(f) for f in links])


    async def opend(self, d: OpenDirectory):
        # TODO: Have the files download as soon as they are fetched
        files = await d.files()
        await self.files(files)
