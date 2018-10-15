import logging
import pickle

import sys
from gensim import similarities
from gensim.corpora import Dictionary
from gensim.models import TfidfModel

from configuration.tfidf.config import TfidfConfig
from model.tfidf.preprocess import Preprocessor
from search_engine.tfidf.logger.logger_config import init_logger


def save(filename, what):
    with open(filename, 'wb') as f:
        pickle.dump(what, f)


def load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


class TfidfEngine(object):
    def __init__(self, max_workers=4, tfidf_model=None, dictionary=None):
        self.log = logging.getLogger('tfidf_search_engine')
        self.tfidf_model = tfidf_model
        self.dictionary = dictionary
        self.preprocessor = Preprocessor(max_workers=max_workers)
        self.index = None
        self.urls = None

    def load_model(self, model_path, dict_path):
        self.log.info("Loading model from %s", model_path)
        self.tfidf_model = TfidfModel.load(model_path)
        self.log.info("Loading dictionary from %s", dict_path)
        self.dictionary = Dictionary.load(dict_path)

    def infer(self, document):
        self.log.info('Infering document "%s"', document[:20] + "..." if len(document) > 20 else document[:20])
        text = self.preprocessor.preprocess_doc(document)
        bow = self.dictionary.doc2bow(text)
        return self.tfidf_model[bow]

    def infer_all(self, docs_with_urls):
        self.log.info("Infering %d documents ", len(docs_with_urls))
        preproc_docs_with_urls = self.preprocessor.process_docs_with_urls(docs_with_urls)
        bags_of_words = [(url, self.dictionary.doc2bow(doc)) for url, doc in preproc_docs_with_urls]
        return [(url, self.tfidf_model[bow]) for url, bow in bags_of_words]

    def dummy_index(self, docs_with_urls):
        self.log.info("Creating index out of %d documents", len(docs_with_urls))
        urls, doc_bows = zip(*self.infer_all(docs_with_urls))
        self.urls = urls
        self.index = similarities.SparseMatrixSimilarity(doc_bows, num_features=len(self.dictionary))

    def save_index(self, index_path, url_path):
        self.log.info("Saving index to %s", index_path)
        self.index.save(index_path)
        self.log.info("Saving urls to %s", url_path)
        save(url_path, self.urls)

    def load_index(self, index_path, url_path):
        self.log.info("Loading index from %s", index_path)
        self.index = similarities.SparseMatrixSimilarity.load(index_path)
        self.log.info("Loading urls from %s", url_path)
        self.urls = load(url_path)

    def search(self, query):
        self.log.info("Searching for documents similar to %s", query)
        infer_query = self.infer(query)
        inferred = self.index[infer_query]
        ss = sorted(enumerate(inferred), key=lambda item: -item[1])
        return [(self.urls[i], sim) for i, sim in ss]

    def dict_search(self, query, results=100):
        infer_query = self.infer(query)
        inferred = self.index[infer_query]
        inferred = sorted(enumerate(inferred), key=lambda item: -item[1])[:results]

        query_len = len(query.split(" "))
        return {self.urls[i]: self.adjust(query_len, sim) for i, sim in inferred}

    def adjust(self, query_length, similarity):
        return similarity * ((4 / query_length) ** 2) if query_length > 4 else similarity

    @staticmethod
    def with_loaded_model():
        init_logger()

        config = TfidfConfig(sys.argv[1], 'tfidf_search_engine').get_current_config()

        searchEngine = TfidfEngine()
        searchEngine.load_model(config['model_path'], config['dict_path'])

        searchEngine.load_index(config['index_path'], config['url_path'])
        return searchEngine
