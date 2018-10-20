import json
from os import listdir
from os.path import isfile, join

import logging

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, directories, encoding):
        self.directories = directories
        self.encoding = encoding

    def parse_json_from_directories(self):
        logger.info("Parsing json documents")
        docs = []
        for directory in self.directories:
            docs = docs + self.parse_json(directory)
        return docs

    def parse_json(self, directory_path):
        files = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]
        documents = []
        for num, file in enumerate(files):
            if num > 1000:
                break
            with open(directory_path + '/' + file, encoding=self.encoding) as f:
                data = json.load(f)

                content = try_parse(data, 'title') + ' ' + \
                          ' '.join(try_parse(data, 'author')) + ' ' + \
                          try_parse(data, 'description') + ' ' + \
                          try_parse(data, 'content')
                documents.append((data['url'], content))
        return documents


def try_parse(data, field):
    try:
        return data[field]
    except:
        return ''
