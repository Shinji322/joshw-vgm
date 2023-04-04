from db import build
from opend.downloader import Downloader
from opend.file import File
from search.game import search, fzf_search_db, fzf_query_consoles
from argparse import ArgumentParser
import asyncio
import sys


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
    if len(sys.argv[1:]) < 0:
        console = fzf_query_consoles()

    if args.build:
        await build()
    if args.search:
        print(search(args.search))
    if args.fuzz:
        game = fzf_search_db()
        if game is None:
            exit(1)
        if input(f"Should I download '{game}'? [y/N]") == "y":
            d = Downloader()
            await d.file(File(game.link))

if __name__ == "__main__":
    asyncio.run(main())
