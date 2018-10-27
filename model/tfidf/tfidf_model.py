import logging

from gensim.corpora import Dictionary
from gensim.models import TfidfModel

logger = logging.getLogger(__name__)


class TFIDF(object):
    def __init__(self,
                 max_workers):
        self.max_workers = max_workers
        self.log = logging.getLogger('tfidf_model')
        self.model, self.dictionary = None, None

    # @timed
    def train(self, preprocessed_docs):
        logger.info('Building dictionary')
        self.dictionary = Dictionary(preprocessed_docs)

        logger.info('Dictionary built with %d words. Building corpus', len(self.dictionary))
        corpus = [self.dictionary.doc2bow(line) for line in preprocessed_docs]  # convert dataset to BoW format

        logger.info('Built corpus')
        self.model = TfidfModel(corpus)

    def save_model(self, model_path):
        logger.info('Saving TFIDF model to file: %s', model_path)
        self.model.save(model_path)

    def save_dictionary(self, dict_path):
        logger.info('Saving dictionary to file: %s', dict_path)
        self.dictionary.save(dict_path)

    def build_corpus(self, doc_list, dictionary):
        return list(map(dictionary.doc2bow, doc_list))

    @staticmethod
    def with_url_handling(max_workers):
        return TFIDF(max_workers)
