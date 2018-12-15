import json
from logging import getLogger
from os import environ
import itertools

import numpy as np
import time
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore

from configuration.config import Config
from preprocessing.preprocessor import Preprocessor

logger = getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def to_dense(array, size):
    arr = np.zeros(size)
    for ind, val in array:
        arr[ind] = val
    return arr


def parse(file):
    with open(file, "r", encoding='utf-8', errors='replace') as f:
        data = json.load(f)
        content = data['title'] + ' ' + \
                  data['description'] + ' ' + \
                  data['content']

        return content


def parse_txt(file):
    with open(file, 'r') as myfile:
        return myfile.read()


def flatten(arr):
    return list(itertools.chain(*arr))


class SeoBooster(object):
    max_keywords = 7

    def __init__(self, max_workers, topics):
        self.preprocessor = Preprocessor(max_workers=max_workers)
        self.topics = topics
        self.model = None
        self.m_dict = None

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        seo = cls(lda_config['max_workers'], lda_config['topics'])
        seo.load_model(lda_config['model_path'], lda_config['dict_path'])

        return seo

    def load_model(self, model_path, dict_path):
        logger.info("Loading model from {}".format(model_path))
        self.model = LdaMulticore.load(model_path)
        self.m_dict = Dictionary.load(dict_path)

    def compute_similarity(self, text, query):
        text_topics = self._infer(text)
        query_topics = self._infer(query)

        return int(
            cosine_similarity(text_topics, query_topics) * 10000) / 100

    def compute_keywords(self, text, max_keywords=max_keywords, max_words_per_topic=2):
        text_topics = self._infer(text)
        present_topics = self._infer_topics(text_topics, max_words_per_topic)
        keywords_with_weights = flatten([ind_words[1] for ind_words in present_topics])

        best_keywords = sorted(keywords_with_weights, key=lambda word_weight: -word_weight[1])[:max_keywords]
        return [keyword for (keyword, weight) in best_keywords]

    @timeit
    def words_to_add_full(self, text, query, max_keywords=max_keywords, max_words_per_topic=3):
        text_inferred = self._infer(text)
        query_inferred = self._infer(query)

        diff = query_inferred - text_inferred
        # zeros negative numbers. There are to many words from these topics, so we don't want to add more
        diff[diff < 0] = 0

        def compute_full_score(topic_words):
            index, weighted_words = topic_words
            return sorted(
                [(word, self.compute_similarity(text + " " + word, query))
                 for (word, weight)
                 in weighted_words],
                key=lambda word_similarity: word_similarity[1],
                reverse=True)[:max_words_per_topic]

        diff_topics = self._infer_topics(diff)

        weighted_words = flatten([compute_full_score(topic_words) for topic_words in diff_topics])

        return [
                   word
                   for (word, score)
                   in sorted(weighted_words,
                             key=lambda x: x[1],
                             reverse=True)][:max_keywords]
    @timeit
    def words_to_add(self, text, query, max_keywords=max_keywords, max_words_per_topic=3):
        text_inferred = self._infer(text)
        query_inferred = self._infer(query)
        diff = query_inferred - text_inferred

        # zeros negative numbers. There are to many words from these topics, so we don't want to add more
        diff[diff < 0] = 0

        def compute_simpified_score(index, weight):
            return weight * diff[index] ** 2

        def truncate_words(topic_words):
            index, weighted_words = topic_words
            return sorted(
                [(word, compute_simpified_score(index, weight))
                 for (word, weight)
                 in weighted_words],
                key=lambda word_score: word_score[1],
                reverse=True)[:max_words_per_topic]

        diff_topics = self._infer_topics(diff)

        weighted_words = flatten([truncate_words(topic_words) for topic_words in diff_topics])

        return [
                   word
                   for (word, score)
                   in sorted(weighted_words,
                             key=lambda x: x[1],
                             reverse=True)][:max_keywords]

    def _infer_topics(self, text_topics, max_words_per_topic=max_keywords):
        topics = sorted(self.model.show_topics(num_topics=self.topics, num_words=max_words_per_topic, formatted=False),
                        key=lambda topic_num_and_words: topic_num_and_words[0])  # set topics in order
        present_topics = [
            (index,
             sorted(words_with_weights, key=lambda word_with_weights: -word_with_weights[1])[:max_words_per_topic])
            for (index, words_with_weights)
            in topics
            if text_topics[index]
        ]

        return present_topics

    def _infer(self, query, dense=True):
        processed_file = self.preprocessor.preprocess_doc(query)

        bow = self.m_dict.doc2bow(processed_file)

        return to_dense(self.model[bow], self.topics) if dense else self.model[bow]
