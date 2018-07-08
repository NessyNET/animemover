FROM python:3

ADD filemover/filemover.py /
ADD filemover/fileparser.py /

CMD ["python", "./filemover.py"]