from db import build
import asyncio


async def main():
    await build(links='assets/links.min.json')

if __name__ == "__main__":
    asyncio.run(main())
