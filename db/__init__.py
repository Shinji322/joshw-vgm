from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import DeclarativeBase

import json
import logging as log

from utils import basename
from opend import OpenDirectory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "Console"

    id = Column(Integer, primary_key=True)
    filename = Column(String(100))
    console = Column(String(10))

    def __init__(self, file, console) -> None:
        self.filename = file
        self.console = console

    def __repr__(self) -> str:
        return f"Game(id={self.id}, filename={self.filename})"

async def build(links='assets/links.json', db='games.db'):
    engine = create_engine(f"sqlite:///{db}", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    with open(links) as f:
        data = json.load(f)
    for k, v in data.items():
        d = OpenDirectory(k)
        print(d)
        files = await d.get_all_files()
        for f in files:
            session.add(Game(basename(f), v))
            session.commit()
