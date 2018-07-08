import re

ANIME_FILE_REGEX = '\[([\w-]+)](?:\s|_)(.*)(?:\s|_)-(?:\s|_)?([0-9]{1,4}).*'


def extract_anime_name(filename):
    m = re.search(ANIME_FILE_REGEX, filename)
    return m.group(2) if m is not None else None
