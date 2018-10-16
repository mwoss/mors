import logging
import pickle

from os import environ

from gensim import similarities
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore

from configuration.config import Config
from configuration.logger_uttils import init_logger
from model.lda.preprocess import Preprocessor
from search_engine.search_engine import SearchEngine


def save(filename, what):
    with open(filename, 'wb') as f:
        pickle.dump(what, f)


def load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


logger = init_logger(__name__)


class LdaEngine(SearchEngine):
    def __init__(self, topics, max_workers=4, lda_model=None, dictionary=None):
        self.topics = topics
        self.lda_model = lda_model
        self.dictionary = dictionary
        self.preprocessor = Preprocessor(max_workers=max_workers)
        self.index = None
        self.urls = None

    def load_model(self, model_path, dict_path):
        logger.info("Loading model from %s", model_path)
        self.lda_model = LdaMulticore.load(model_path)
        self.dictionary = Dictionary.load(dict_path)

    def save_index(self, index_path, url_path):
        self.log.info("Saving index to %s", index_path)
        self.index.save(index_path)
        save(url_path, self.urls)

    def load_index(self, index_path, url_path):
        self.log.info("Loading index from %s", index_path)
        self.index = similarities.SparseMatrixSimilarity.load(index_path)
        self.log.info("Loading urls from %s", url_path)
        self.urls = load(url_path)

    def infer(self, document):
        self.log.info('Infering document "%s"', document[:20] + "..." if len(document) > 20 else document[:20])
        text = self.preprocessor.preprocess_doc(document)
        bow = self.dictionary.doc2bow(text)
        return self.lda_model[bow]

    def infer_all(self, docs_with_urls):
        self.log.info("Infering %d documents ", len(docs_with_urls))
        preproc_docs_with_urls = self.preprocessor.process_docs_with_urls(docs_with_urls)
        bags_of_words = [(url, self.dictionary.doc2bow(doc)) for url, doc in preproc_docs_with_urls]
        return [(url, self.lda_model[bow]) for url, bow in bags_of_words]

    def create_index(self, docs_with_urls):
        self.log.info("Creating index out of %d documents", len(docs_with_urls))
        urls, doc_bows = zip(*self.infer_all(docs_with_urls))
        self.urls = urls
        self.index = similarities.SparseMatrixSimilarity(doc_bows, num_features=self.topics)

    def search(self, query):
        self.log.info("Searching for documents similar to %s", query)
        inferred = self.index[self.infer(query)]
        ss = sorted(enumerate(inferred), key=lambda item: -item[1])
        return [(self.urls[i], sim) for i, sim in ss]

    def dict_search(self, query, results=100):
        inferred = self.index[self.infer(query)]
        inferred = sorted(enumerate(inferred), key=lambda item: -item[1])[:results]

        query_len = len(query.split(" "))
        return {self.urls[i]: self._adjust(query_len, sim) for i, sim in inferred}

    def _adjust(self, query_length, similarity):
        return similarity / ((5 - query_length) ** 2) if query_length < 4 else similarity

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        search_engine = cls(lda_config['topics'])
        search_engine.load_model(lda_config['model_path'], lda_config['dict_path'])
        search_engine.load_index(lda_config['index_path'], lda_config['url_path'])

        return search_engine
