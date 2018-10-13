import json
import logging

import os

from codecs import open

log = logging.getLogger('lda_model')


def parse_wiki_dump(filename, limit=None):
    texts = []
    buffer = []
    with open(filename, "r", encoding='utf-8', errors='replace') as f:
        for line in f.readlines():
            if line.startswith(" =") and line.endswith("= \n") and line.count('=') == 2:
                if buffer:
                    texts.append(''.join(buffer))
                    buffer = []
                    if limit and limit < len(texts):
                        return texts[1:]
            trimmed_line = line.replace('<unk>', '')
            buffer.append(trimmed_line)
        if buffer:
            texts.append(''.join(buffer))
    return texts[1:]


def parse_dir_json(dirpath, limit=None):
    documents = []
    dirs = next(os.walk(dirpath))[1]
    for dir in dirs:
        sub_dirpath = dirpath + dir
        for file in os.listdir(sub_dirpath):
            try:
                with open(sub_dirpath + '/' + file, "r", encoding='utf-8', errors='replace') as f:
                    data = json.load(f)
                    content = try_parse(data, 'title') + ' ' + \
                              ' '.join(try_parse(data, 'author')) + ' ' + \
                              try_parse(data, 'description') + ' ' + \
                              try_parse(data, 'content')

                    documents.append((data['url'], content))
                if limit is not None and len(documents) > limit:
                    return documents
            except:
                log.error('Could not parse file: %s', file)
    return documents


def try_parse(data, field):
    try:
        return data[field]
    except:
        return ''
