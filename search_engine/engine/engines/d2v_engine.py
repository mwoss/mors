from logging import getLogger
from os import environ

from gensim.models.doc2vec import Doc2Vec

from search_engine.configuration.config import Config
from search_engine.preprocessing.preprocessor import Preprocessor
from search_engine.engine.search_engine import SearchEngine

logger = getLogger(__name__)


class D2VEngine(SearchEngine):
    def __init__(self, max_workers=4):
        super().__init__()
        self.preprocessor = Preprocessor(max_workers=max_workers)

    @classmethod
    def from_configfile(cls):
        profile = environ.get('d2v_profile', 'local')
        config = Config(profile).d2v

        search_engine = cls()
        search_engine.load_model(config['dbow_model_path'])
        return search_engine

    def load_model(self, model_path, dict_path=None):
        self.model = Doc2Vec.load(model_path)

    def search(self, query, limit=50):
        inferred_vector = self._infer(query)
        return self.model.docvecs.most_similar([inferred_vector], topn=limit)

    def dict_search(self, query, limit=100):
        limit = self.search(query, limit=limit)

        query_len = len(query.split(" "))
        return {url: self._adjust(query_len, similarity) for url, similarity in limit}

    def _infer(self, document):
        tokens = self.preprocessor.preprocess_doc(document)
        return self.model.infer_vector(tokens, alpha=0.001, steps=40)

    def _adjust(self, query_length, similarity):
        return similarity / ((5 - query_length) ** 2) if query_length < 4 else similarity
