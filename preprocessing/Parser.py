import json
from os import listdir
from os.path import isfile, join


class Parser(object):
    MAX_DOCS_PER_DIR = 1000

    def __init__(self, directories, encoding):
        self.directories = directories
        self.encoding = encoding

    def parse_articles_from_directories(self):
        for directory in self.directories:
            yield from self._parse_articles(directory)

    def _parse_articles(self, directory_path):
        files = [file for file in listdir(directory_path) if isfile(join(directory_path, file))]

        for file in files[:self.MAX_DOCS_PER_DIR]:
            with open(directory_path + '/' + file, encoding=self.encoding) as f:
                data = json.load(f)

                content = data['title'] + ' ' + data['description'] + ' ' + data['content']
                yield (data['url'], content)
