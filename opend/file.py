from pathlib import Path
from utils import unq


class File:
    def __init__(self, p: str) -> None:
        """
        A class for wrapping some pathlib functionality
        
        @param p: String location of the file path
        """
        self.url = p
        self.path = Path(p)


    @property
    def name(self) -> str:
        """
        Returns the base filename
        """
        return unq(self.path.name)


    @property
    def basename(self) -> str:
        return unq(self.name)


    def tree(self, start:int, end:int=None): # pyright: ignore
        """
        It returns the path along the given range split on '/'
        """
        return '/'.join(self.url.split('/')[start:end])


    @property
    def filename(self) -> str:
        """
        'https://usf.joshw.info/b/Bakuretsu Muteki Bangai-O (1999-09-03)(Treasure)(ESP)[N64].7z' -> 'b/Bakuretsu Muteki Bangai-O (1999-09-03)(Treasure)(ESP)[N64].7z'
        """
        return self.tree(-2)


    def exists(self) -> bool:
        return self.path.exists()


    def touch(self) -> None:
        """
        Creates the appropriate parent directories andd then touches the file
        """
        # Any parent directories should be made
        d = Path(self.tree(-2, -1))
        if not d.exists():
            d.mkdir(parents=True)

        # Touch the file
        f = Path(self.filename)
        f.touch()


    def __str__(self) -> str:
        return f"{self.url}"


    def __hash__(self) -> int:
        return hash(str(self))


def main():
    f = File("https://usf.joshw.info/b/Bakuretsu Muteki Bangai-O (1999-09-03)(Treasure)(ESP)[N64].7z")
    print(f.url)


if __name__ == "__main__":
    main()
