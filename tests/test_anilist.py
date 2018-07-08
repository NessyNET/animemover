from filemover.fileparser import FileParser


def test_extract_anime_name_positive():
    fileparser = FileParser()
    with open('testdata_fileparser.txt', 'rU') as f:
        for line in f:
            (filename, name) = line.split('::')
            match = fileparser.extract_anime_name(filename.strip())

            assert match
            assert (match == name.strip())
