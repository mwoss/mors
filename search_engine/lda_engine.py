from logging import getLogger
from os import environ

from gensim import similarities
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore

from configuration.config import Config
from preprocessing.preprocessor import Preprocessor
from search_engine.search_engine import HybridEngine

logger = getLogger(__name__)


class LdaEngine(HybridEngine):
    def __init__(self, topics, max_workers=4):
        super().__init__()
        self.topics = topics
        self.preprocessor = Preprocessor(max_workers=max_workers)

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        search_engine = cls(lda_config['topics'])
        search_engine.load_model(lda_config['model_path'], lda_config['dict_path'])
        search_engine.load_index(lda_config['index_path'], lda_config['url_path'])

        return search_engine

    def load_model(self, model_path, dict_path):
        logger.info("Loading model from {}".format(model_path))
        self.model = LdaMulticore.load(model_path)
        self.dictionary = Dictionary.load(dict_path)

    def create_index(self, docs_with_urls):
        logger.info("Creating index out of {} documents".format(len(docs_with_urls)))
        urls, doc_bows = zip(*self.infer_all(docs_with_urls))
        self.urls = urls
        self.index = similarities.SparseMatrixSimilarity(doc_bows, num_features=self.topics)

    def _adjust(self, query_length, similarity):
        return similarity / ((5 - query_length) ** 2) if query_length < 4 else similarity
