import logging
import sys

from gensim.models.doc2vec import Doc2Vec

from configuration.doc2vec.config import Doc2VecConfig
from model.lda.preprocess import Preprocessor

logger = logging.getLogger(__name__)


class D2VEngine(object):
    def __init__(self, max_workers=4):
        self.model = None
        self.preprocessor = Preprocessor(max_workers=max_workers)

    def load_model(self, model_path):
        logger.info("Loading model from %s", model_path)
        self.model = Doc2Vec.load(model_path)

    def infer(self, query):
        tokens = self.preprocessor.preprocess_doc(query)
        logger.info("Inferring vector %s", tokens)
        return self.model.infer_vector(tokens, alpha=0.001, steps=40)

    def search(self, query, results=100):
        logger.info("Searching for document similar to: %s", query)
        inferred_vector = self.infer(query)
        return self.model.docvecs.most_similar([inferred_vector], topn=results)

    def dict_search(self, query, results=100):
        results = self.search(query, results=results)

        query_len = len(query.split(" "))
        return {url: self.adjust(query_len, similarity) for url, similarity in results}

    def adjust(self, query_length, similarity):
        return similarity / ((5 - query_length) ** 2) if query_length < 4 else similarity

    @staticmethod
    def with_loaded_model():
        config = Doc2VecConfig(sys.argv[1]).get_configuration()

        search_engine = D2VEngine()
        search_engine.load_model(config['dbow_model_path'])
        return search_engine
