import os
import logging as log

def basename(link:str) -> str:
    """
    Returns the basename of the link
    """
    log.fatal(f"link: {link}")
    return os.path.basename(link)
