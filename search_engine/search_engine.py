from gensim.similarities import SparseMatrixSimilarity

from model.model import EmptyModel, EmptyIndex, save_model, load_model


class SearchEngineMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj._is_preprocessor_set()
        return obj


class SearchEngine(metaclass=SearchEngineMeta):
    def __init__(self):
        self.model, self.dictionary = (EmptyModel(),) * 2
        self.index, self.urls = (EmptyIndex(),) * 2
        self.preprocessor = None

    def _is_preprocessor_set(self):
        if self.preprocessor is None:
            raise NotImplementedError('Subclasses must define own preprocessor')

    @classmethod
    def from_configfile(cls):
        raise NotImplementedError

    def search(self, query, results):
        raise NotImplementedError

    def dict_search(self, query, results):
        raise NotImplementedError

    def load_model(self, model_path, dict_path):
        raise NotImplementedError

    def _infer(self, document):
        raise NotImplementedError

    def _adjust(self, query_length, similarity):
        raise NotImplementedError


class HybridEngine(SearchEngine):
    def search(self, query, results):
        inferred = self.index[self._infer(query)]
        inferred = sorted(enumerate(inferred), key=lambda item: -item[1])[:results]
        return [(self.urls[i], sim) for i, sim in inferred]

    def dict_search(self, query, results):
        inferred = self.index[self._infer(query)]
        inferred = sorted(enumerate(inferred), key=lambda item: -item[1])[:results]

        query_len = len(query.split(" "))
        return {self.urls[i]: self._adjust(query_len, sim) for i, sim in inferred}

    def load_index(self, index_path, url_path):
        self.index = SparseMatrixSimilarity.load(index_path)
        self.urls = load_model(url_path)

    def save_index(self, index_path, url_path):
        self.index.save(index_path)
        save_model(url_path, self.urls)

    def _infer(self, document):
        text = self.preprocessor.preprocess_doc(document)
        bow = self.dictionary.doc2bow(text)
        return self.model[bow]

    def infer_all(self, docs_with_urls):
        preproc_docs_with_urls = self.preprocessor.process_docs_with_urls(docs_with_urls)
        bags_of_words = [(url, self.dictionary.doc2bow(doc)) for url, doc in preproc_docs_with_urls]
        return [(url, self.model[bow]) for url, bow in bags_of_words]

    def load_model(self, model_path, dict_path):
        raise NotImplementedError

    def create_index(self, docs_with_urls):
        raise NotImplementedError

    @classmethod
    def from_configfile(cls):
        raise NotImplementedError

    def _adjust(self, query_length, similarity):
        raise NotImplementedError
