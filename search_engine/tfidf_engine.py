from os import environ

from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import SparseMatrixSimilarity

from configuration.config import Config
from configuration.logger_uttils import init_logger
from model.tfidf.preprocess import Preprocessor
from search_engine.search_engine import HybridEngine

logger = init_logger(__name__)


class TfidfEngine(HybridEngine):
    def __init__(self, max_workers=4):
        super().__init__()
        self.preprocessor = Preprocessor(max_workers=max_workers)

    @classmethod
    def from_configfile(cls):
        profile = environ.get('tfidf_profile', 'local')
        tfidf_config = Config(profile=profile).tfidf

        search_engine = cls()
        search_engine.load_model(tfidf_config['model_path'], tfidf_config['dict_path'])
        search_engine.load_index(tfidf_config['index_path'], tfidf_config['url_path'])

        return search_engine

    def load_model(self, model_path, dict_path):
        logger.info("Loading model from {}".format(model_path))
        self.model = TfidfModel.load(model_path)
        self.dictionary = Dictionary.load(dict_path)

    def create_index(self, docs_with_urls):
        logger.info("Creating index out of {} documents".format(len(docs_with_urls)))
        urls, doc_bows = zip(*self.infer_all(docs_with_urls))
        self.urls = urls
        self.index = SparseMatrixSimilarity(doc_bows, num_features=len(self.dictionary))

    def _adjust(self, query_length, similarity):
        return similarity * ((4 / query_length) ** 2) if query_length > 4 else similarity
