from db import Game, SQLEngine

def search(query: str):
    session = SQLEngine().make_session()
    return session.query(Game).filter(Game.name.like(query))
