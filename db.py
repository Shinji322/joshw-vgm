from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, String, Column
from sqlalchemy import create_engine
from opend import OpenDirectory
from opend.file import File
from config import DB_FILE
import json


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = 'Games'

    id = Column('id', Integer, primary_key=True)
    link = Column('link', String)
    name = Column('name', String)
    console = Column('console', String)

    def __init__(self, f: File, console: str) -> None:
        self.link = f.fullname
        self.name = f.basename
        self.console = console

    def __repr__(self) -> str:
        return f"Game(id={self.id}, filename={self.name})"

    def __hash__(self) -> int:
        return hash(f"{self.name} {self.link} {self.console}")


# A helper class to wrap my bad code
class SQLEngine:
    def __init__(self, db=DB_FILE) -> None:
        self.db = db
        self.__init_engine()


    def __init_engine(self):
        self.engine = create_engine(f"sqlite:///{self.db}", echo=True)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)


    def make_session(self):
        return self.Session()


async def build(links='assets/links.json', db=DB_FILE):
    session = SQLEngine(db).make_session()

    with open(links) as f:
        data = json.load(f)
    for link, console in data.items():
        files = await OpenDirectory(link).files()
        for f in files:
            game = Game(f, console)
            session.add(game)
        session.commit()
