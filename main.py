from db import build
from opend.downloader import Downloader
from opend.file import File
from search.query import Query, FZF
from argparse import ArgumentParser
import logging as log
import asyncio
import sys

log.disable(log.CRITICAL)

async def main():
    """
    The main entrypoint for the program
    """
    p = ArgumentParser(prog='vgm', description='download video game music from joshw!')
    p.add_argument('-b', '--build', help='build the database (this should be run before any other command has been run)', action='store_true')
    p.add_argument('-a', '--add-opend', help='adds an open directory to the database', nargs=1)
    p.add_argument('-s', '--search', help='query the database', nargs=1)
    p.add_argument('-f', '--fuzz', help='fuzzy search the database', action='store_true')
    args = p.parse_args()
    if len(sys.argv[1:]) <= 0:
        console = FZF.consoles()
        FZF.consoles(Query.console(console))

    if args.build:
        await build()
    if args.search:
        Query.name(args.search)
    if args.fuzz:
        game = FZF.search()
        if game is None:
            exit(1)
        if input(f"Should I download '{game}'? [y/N] ") == "y":
            d = Downloader()
            print(f"Downloading: {game}")
            await d.file(File(game.link))

if __name__ == "__main__":
    asyncio.run(main())
