from urllib.parse import unquote
import os
import logging as log

def basename(link:str) -> str:
    """
    Returns the basename of the link
    """
    log.fatal(f"link: {link}")
    return os.path.basename(link)

def unq(link:str) -> str:
    """
    Decodes urls
        example.com?title=%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D0%B2%D0%B0%D1%8F+%D0%B7%D0%B0%D1%89%D0%B8%D1%82%D0%B0 -> example.com?title==правовая+защита
    """
    return unquote(link)
