from db import build
import asyncio

async def main():
    await build()

if __name__ == "__main__":
    asyncio.run(main())
