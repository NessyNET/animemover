import os
import logging
import time

import fileparser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
allowed_ext = ['.avi', '.mkv', '.mp4']


def main():
    input = '/input'
    output = '/output'
    logger.info("Animemover has been started")
    while True:
        time.sleep(5*60)
        for filepath in os.listdir(input):
            source = os.path.join(os.getcwd(), input, filepath)
            if not os.path.isdir(source) and os.path.splitext(filepath)[1] in allowed_ext:
                movefile(source, output, filepath)


def movefile(source, output, filepath):
    anime = fileparser.extract_anime_name(filepath)
    if anime:
        logger.info('Candidate file %s', filepath)
        target = os.path.join(os.getcwd(), output, anime)
        if not os.path.exists(target):
            os.mkdir(target)
        if os.path.isdir(target):
            logger.info('Moving anime %s :: %s', anime, filepath)
            os.rename(source, os.path.join(target, filepath))
        else:
            logger.error("Unable to move [%s] but the target location [%s] isn't a directory", filepath,
                         target)


if __name__ == '__main__':
    main()
