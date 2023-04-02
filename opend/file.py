from pathlib import Path
from utils import unq


class File:
    def __init__(self, p: str) -> None:
        """
        A class for wrapping some pathlib functionality
        """
        self.path = Path(p)


    @property
    def fullname(self) -> str:
        """
        Returns the full filepath
        """
        return str(self.path.absolute())


    @property
    def name(self) -> str:
        """
        Returns the base filename
        """
        return unq(self.path.name)

    @property
    def basename(self) -> str:
        return unq(self.name)



    @property
    def relativename(self) -> str:
        """
        'https://usf.joshw.info/b/Bakuretsu Muteki Bangai-O (1999-09-03)(Treasure)(ESP)[N64].7z' -> 'b/Bakuretsu Muteki Bangai-O (1999-09-03)(Treasure)(ESP)[N64].7z'
        """
        return self.tree(-2)


    def tree(self, start:int, end:int=None): # pyright: ignore
        """
        It returns the path along the given range split on '/'
        """
        return '/'.join(self.fullname.split('/')[start:end])


    def touch(self) -> None:
        """
        Creates the appropriate parent directories andd then touches the file
        """
        Path(self.tree(-2, -1)).mkdir(parents=True)
        self.path.touch()


    def __str__(self) -> str:
        return f"{self.fullname}"


    def __hash__(self) -> int:
        return hash(str(self))


def main():
    f = File("https://usf.joshw.info/b/Bakuretsu Muteki Bangai-O (1999-09-03)(Treasure)(ESP)[N64].7z")
    print(f.tree(-2))


if __name__ == "__main__":
    main()
