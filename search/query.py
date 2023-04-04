from collections.abc import Iterable
from search.fzf import FzfPrompt
from sqlmodel import Session, col, select
from db import Game, engine

class Query:
    @staticmethod
    def name(query: str):
        with Session(engine) as session:
            s = select(Game).filter(col(Game.name).contains(f"%{query}%"))
            return session.exec(s)


    @staticmethod
    def console(query: str):
        with Session(engine) as session:
            s = select(Game).filter(Game.console == query)
            return session.exec(s)

class FZF:
    @staticmethod
    def search() -> Game | None:
        p = FzfPrompt()
        with Session(engine) as session:
            name = p.prompt([str(i) for i in session.exec(select(Game))])[0]
            s = select(Game).where(Game.name == name)
            return session.exec(s).first()

    @staticmethod
    def select(l: Iterable):
        p = FzfPrompt()
        choices = [str(v) for v in l]
        return p.prompt(choices)


    @staticmethod
    def consoles() -> str:
        p = FzfPrompt()
        choices = [
            "PC",
            "FM",
            "Hoot",
            "S98",
            "MSX",
            "NES",
            "SNES",
            "N64",
            "Gamecube",
            "Wii" ,
            "Wii U",
            "Sega CD/Master Drive",
            "Sega Saturn",
            "Dreamcast",
            "PC Engine",
            "Neo Geo",
            "PSX",
            "PS2",
            "PS3",
            "XBox",
            "XBox360",
            "3DO",
            "Gameboy",
            "GBA",
            "DS",
            "3DS" ,
            "Wonder swan",
            "PSP",
            "Vita" 
        ]
        return p.prompt(choices)[0]
