from typing import Optional
from sqlmodel import Field, SQLModel, Session, create_engine
from opend import OpenDirectory
from opend.file import File
from config import DB_FILE
import json

engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)


class Game(SQLModel, table=True):
    id:  Optional[int] = Field(default=None, primary_key=True)
    name: str
    link: str
    console: str

    def __init__(self, f: File, console: str) -> None:
        self.link = f.fullname
        self.name = f.basename
        self.console = console

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"Game(id={self.id}, filename={self.name})"

    def __hash__(self) -> int:
        return hash(f"{self.name} {self.link} {self.console}")

    def __eq__(self,other) -> bool:
        return self.link == other.link and self.name == other.name and self.console == other.console


async def build(links='assets/links.json'):
    SQLModel.metadata.create_all(engine)

    with open(links) as f:
        data = json.load(f)
    with Session(engine) as session:
        for link, console in data.items():
            files = await OpenDirectory(link).files()
            for f in files:
                game = Game(f, console)
                session.add(game)
            session.commit()
