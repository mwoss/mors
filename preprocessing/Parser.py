import json
from os import listdir
from os.path import isfile, join


class Parser(object):
    def __init__(self, directories, encoding):
        self.directories = directories
        self.encoding = encoding

    def parse_articles_from_directories(self):
        docs = []
        for directory in self.directories:
            docs = docs+self.parse_articles(directory)
        return docs

    def parse_articles(self, directory_path):
        files = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]
        documents = []
        for num, file in enumerate(files):
            if num > 1000:
                break
            with open(directory_path + '/' + file, encoding=self.encoding) as f:
                data = json.load(f)

                content = data['title'] + ' ' + data['description'] + ' ' + data['content']
                documents.append((data['url'], content))
        return documents
