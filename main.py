from db import build
from search.game import search
import asyncio
from argparse import ArgumentParser


async def main():
    """
    The main entrypoint for the program
    """
    #p = ArgumentParser(prog='vgm', description='download video game music from joshw!')
    #p.add_argument('-b', '--build', help='build the database (this should be run before the )')
    #p.add_argument('-a', '--add-opend', help='adds an open directory to the database')
    #p.add_argument('-s', '--search', help='query the dataabse')
    #p.add_argument('-f', '--fuzzy-search', help='fuzzy search the database')
    #args = p.parse_args()
    #await build(links='assets/links.json')
    print(search("Mario"))

if __name__ == "__main__":
    asyncio.run(main())
