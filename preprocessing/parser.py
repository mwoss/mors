import json
import logging
from os import listdir
from os.path import isfile, join

logger = logging.getLogger(__name__)


class Parser(object):
    MAX_DOCS_PER_DIR = 1000

    def __init__(self, directories, encoding):
        self.directories = directories
        self.encoding = encoding

    def parse_articles_from_directories(self):
        docs = []
        for directory in self.directories:
            docs = docs + self._parse_articles(directory)
        return docs

    def _parse_articles(self, directory_path):
        documents = []
        files = [file for file in listdir(directory_path) if isfile(join(directory_path, file))]

        for file in files[:self.MAX_DOCS_PER_DIR]:
            with open(directory_path + '/' + file, encoding=self.encoding) as f:
                data = json.load(f)

                content = data['title'] + ' ' + data['description'] + ' ' + data['content']
                documents.append((data['url'], content))
        return documents


def try_parse(data, field):
    try:
        return data[field]
    except Exception:
        return ''
