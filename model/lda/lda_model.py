import logging
from concurrent.futures import ProcessPoolExecutor
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore

logger = logging.getLogger(__name__)


class LDA(object):
    def __init__(self, max_workers,
                 num_topics,
                 passes):
        self.passes = passes
        self.num_topics = num_topics
        self.max_workers = max_workers
        self.model, self.dictionary = None, None

    def train(self, preprocessed_docs):
        logger.info('Building dictionary')
        self.dictionary = Dictionary(preprocessed_docs)
        logger.info('Dictionary built with %d words. Building corpus', len(self.dictionary))
        corpus = self.build_corpus(preprocessed_docs, self.dictionary)
        logger.info('Built corpus. Starting actual training with '
                      '%d topics, %d workers, %d passes', self.num_topics, self.max_workers, self.passes)
        self.model = LdaMulticore(corpus,
                                  num_topics=self.num_topics,
                                  id2word=self.dictionary,
                                  workers=self.max_workers,
                                  passes=self.passes)

    def save_model(self, model_path):
        logger.info('Saving LDA model to file: %s', model_path)
        self.model.save(model_path)

    def save_dictionary(self, dict_path):
        logger.info('Saving dictionary to file: %s', dict_path)
        self.dictionary.save(dict_path)

    def build_corpus(self, doc_list, dictionary):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(dictionary.doc2bow, doc_list))

    @staticmethod
    def with_url_handling(max_workers,
                          num_topics,
                          passes
                          ):
        return LDA(max_workers,
                   num_topics,
                   passes)
