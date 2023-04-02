from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import DeclarativeBase
from utils import basename, unq
from opend import OpenDirectory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "Console"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    filename = Column('filename', String)
    link = Column('link', String)
    console = Column('console', String)

    def __init__(self, link, console) -> None:
        self.link = link
        self.console = console

        self.filename = basename(self.link)
        self.name = unq(self.filename)

    def __repr__(self) -> str:
        return f"Game(id={self.id}, filename={self.filename})"

    def __hash__(self) -> int:
        return hash(f"{self.filename} {self.link} {self.console}")


async def build(links='assets/links.json', db='games.db'):
    engine = create_engine(f"sqlite:///{db}", echo=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(links) as f:
        data = json.load(f)
    for link, console in data.items():
        files = await OpenDirectory(link).get_all_files()
        for f in files:
            game = Game(f, console)
            session.add(game)
        session.commit()
