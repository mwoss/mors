import logging
from os import environ

import gensim
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore, TfidfModel

from configuration.config import Config
from preprocessing.preprocessor import Preprocessor

logger = logging.getLogger(__name__)


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def to_dense(array, size):
    arr = np.zeros(size)
    for ind, val in array:
        arr[ind] = val
    return arr


class AbstractEvaluator(object):
    def __init__(self, max_workers, topics):
        self.preprocessor = Preprocessor(max_workers=max_workers)
        self.topics = topics
        self.model = None
        self.tfidf_model = None
        self.m_dict = None
        self.config = None

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        abstractSeo = cls(lda_config['max_workers'], lda_config['topics'])
        abstractSeo.load_lda_model(lda_config['model_path'], lda_config['dict_path'])

        return abstractSeo

    def load_lda_model(self, model_path, dict_path):
        logger.info("Loading model from {}".format(model_path))
        self.model = LdaMulticore.load(model_path)
        self.m_dict = Dictionary.load(dict_path)

    def load_tfidf_model(self, model_path, dict_path):
        logger.info("Loading model from {}".format(model_path))
        self.tfidf_model = TfidfModel.load(model_path)
        self.m_dict = Dictionary.load(dict_path)

    def compute_similarity(self, text, query):
        """
        :param text: string with text to compare
        :param query: query as string
        :return: similarity in range [0,100]
        """
        text_topics = self._infer(text,dense=False)
        query_topics = self._infer(query,dense=False)

        return int(
            gensim.matutils.cossim(text_topics, query_topics) * 10000) / 100

    def _infer(self, query, dense=True):
        processed_file = self.preprocessor.preprocess_doc(query)

        bow = self.m_dict.doc2bow(processed_file)

        return to_dense(self.model[bow], self.topics) if dense else self.model[bow]

    def _infer(self, query,model, dense=True):
        processed_file = self.preprocessor.preprocess_doc(query)

        bow = self.m_dict.doc2bow(processed_file)

        return to_dense(model[bow], self.topics) if dense else model[bow]
