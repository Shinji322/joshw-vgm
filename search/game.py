from search.fzf import FzfPrompt
from sqlmodel import Session, col, select
from db import Game, engine

def search(query: str):
    with Session(engine) as session:
        s = select(Game).filter(col(Game.name).contains(f"%{query}%"))
        return session.exec(s)


def fzf_search_db() -> Game | None:
    p = FzfPrompt()
    with Session(engine) as session:
        name = p.prompt([str(i) for i in session.exec(select(Game))])[0]
        s = select(Game).where(Game.name == name)
        return session.exec(s).first()


def fzf_query_consoles() -> str:
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
