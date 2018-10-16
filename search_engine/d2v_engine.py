from os import environ

from configuration.config import Config
from configuration.logger_uttils import init_logger
from search_engine.search_engine import SearchEngine

logger = init_logger(__name__)


class D2VEngine(SearchEngine):
    def dict_search(self, query, results=100):
        pass

    def search(self, query):
        pass

    @classmethod
    def from_configfile(cls):
        profile = environ.get('d2v_profile', 'local')
        config = Config(profile).d2v

        search_engine = cls()
        search_engine._load_model(config['dbow_model_path'])
        return search_engine

    def _load_model(self, model_path, dict_path):
        pass

    def _infer(self, query):
        pass

    def _adjust(self, query_length, similarity):
        return similarity / ((5 - query_length) ** 2) if query_length < 4 else similarity
