from abc import ABC, abstractmethod


class SearchEngine(ABC):

    @abstractmethod
    def dict_search(self, query, results=100):
        pass

    @classmethod
    @abstractmethod
    def from_configfile(cls):
        pass

    @abstractmethod
    def _load_model(self, model_path, dict_path):
        pass

    @abstractmethod
    def _infer(self, query):
        pass

    @abstractmethod
    def _adjust(self, query_length, similarity):
        pass
