import json
import re
from logging import getLogger
from os import environ
import itertools

import gensim
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
    max_keywords = 9
    max_words_per_topic = 3

    def __init__(self, max_workers, topics):
        self.preprocessor = Preprocessor(max_workers=max_workers)
        self.topics = topics
        self.model = None
        self.m_dict = None
        self.d2v=None
        self.d2v_path = None

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        seo = cls(lda_config['max_workers'], lda_config['topics'])
        seo.load_model(lda_config['model_path'], lda_config['dict_path'])
        seo.d2v_path = lda_config['d2v_path']
        print("loaded model with {} topics".format(seo.model.num_topics))

        return seo

    def load_model(self, model_path, dict_path):
        logger.info("Loading model from {}".format(model_path))
        self.model = LdaMulticore.load(model_path)
        self.m_dict = Dictionary.load(dict_path)

    def compute_similarity(self, text, query):
        """
        :param text: string with text to compare
        :param query: query as string
        :return: similarity in range [0,100]
        """
        text_topics = self._infer(text)
        query_topics = self._infer(query)

        return int(
            cosine_similarity(text_topics, query_topics) * 10000) / 100

    def compute_keywords(self, text, max_keywords=max_keywords, max_words_per_topic=max_words_per_topic):
        """
        :param text: string with text to compare
        :param max_keywords: max number of words that will be returned
        :param max_words_per_topic: max number of words that will be returned from 1 topic
        :return: returns keywords derived from text. For each topic existing in text it takes only $max_words_per_topic.
        Then all keywords are sorted by relevance and only $max_keywords most relevant are returned

        """
        text_topics = self._infer(text)
        present_topics = self._infer_topics(text_topics, max_words_per_topic)
        keywords_with_weights = flatten([
            [(word, weight* (text_topics[ind_words[0]]**2)) for (word,weight) in ind_words[1]]
            for ind_words in present_topics])

        best_keywords = sorted([key_weight for key_weight in keywords_with_weights if len(key_weight[0]) >2],
                               key=lambda word_weight: word_weight[1], reverse=True)[
                        :max_keywords]
        return [keyword for (keyword, weight) in best_keywords]

    @timeit
    def words_to_add_full(self, text, query, max_keywords=max_keywords, max_words_per_topic=max_words_per_topic):
        """
        :param text: text to be optimized
        :param query: query for which the text will be optimized
        :param max_keywords: max number of words that will be returned
        :param max_words_per_topic: max number of words that will be returned from 1 topic
        :return: returns $max_keywords words that should be added to :text in order to make it more similar to :query
            The method is "full" which means that each returned word is proven to increase similarity between :text and
            :query when added to :text. One problem that can occur is that it can return words that overfit to given
            example and may not generalize well. However is less generic than the "simple" version and can give more
            interesting results
        """

        def compute_score(topic_words, diff):
            return self._compute_full_score(topic_words, text, query, diff)

        return self._words_to_add(text, query, compute_score, max_keywords=max_keywords,
                                  max_words_per_topic=max_words_per_topic)

    @timeit
    def words_to_add_simple(self, text, query, max_keywords=max_keywords, max_words_per_topic=max_words_per_topic):
        """
        :param text: text to be optimized
        :param query: query for which the text will be optimized
        :param max_keywords: max number of words that will be returned
        :param max_words_per_topic: max number of words that will be returned from 1 topic
        :return: returns $max_keywords words that should be added to :text in order to make it more similar to :query
            The method is "simple" which means that each returned word will possibly increase similarity between :text
            and :query when added to :text. It takes the difference between vectors and returns words that should make
            :text vector shift towards :query vector. It doesn't however check if the shift will be too strong/too weak
            or just accurate. It is faster than the "full" method and is less prone to model overfitting towards some features
            but suggests more generic words.
        """
        return self._words_to_add(text, query, self._compute_simple_score, max_keywords=max_keywords,
                                  max_words_per_topic=max_words_per_topic)

    def _compute_full_score(self, topic_words, text, query, diff):
        index, weighted_words = topic_words
        return sorted(
            [(word, self.compute_similarity(text + " " + word, query))
             for (word, weight)
             in weighted_words],
            key=lambda word_similarity: word_similarity[1],
            reverse=True)

    def _compute_simple_score(self, topic_words, diff):
        def simple_score(index, weight):
            return weight * diff[index] ** 2

        index, weighted_words = topic_words
        return sorted(
            [(word, simple_score(index, weight))
             for (word, weight)
             in weighted_words],
            key=lambda word_score: word_score[1],
            reverse=True)

    def _words_to_add(self, text, query, compute_score, max_keywords=max_keywords,
                      max_words_per_topic=max_words_per_topic):
        text_inferred = self._infer(text)
        query_inferred = self._infer(query)
        diff = query_inferred - text_inferred

        # zeros negative numbers. There are to many words from these topics, so we don't want to add more
        diff[diff < 0] = 0

        diff_topics = self._infer_topics(diff)

        weighted_words = flatten(
            [compute_score(topic_words, diff)[:max_words_per_topic] for topic_words in diff_topics])

        return [
                   word
                   for (word, score)
                   in sorted(weighted_words,
                             key=lambda x: x[1],
                             reverse=True)][:max_keywords]

    def words_to_flip(self,text, query,max_keywprds = max_keywords*2, max_similarities =5):
        if not self.d2v:
            self.load_d2v(self.d2v_path)
        print("initial similarity: {}".format(self.compute_similarity(text,query)))
        result = []
        for word in set([w for w in re.findall(r"[\w']+", text) if len(w) > 2]):
            try:
                synonyms = self.d2v.most_similar(positive=[word],topn=max_similarities)
                best_synonym = max([(synonym,self.compute_similarity(text.replace(word,synonym,1),query)) for (synonym, _) in synonyms],key=lambda x: x[1])
                result.append((word,best_synonym))
            except KeyError:
                print('no words like {} in d2v model'.format(word))

        sorted_result = sorted(result, key=lambda x: x[1][1],reverse=True)[:max_keywprds]

        return {before_word : after_word for (before_word,(after_word,res)) in sorted_result}

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

    def load_d2v(self, d2v_path):
        self.d2v = gensim.models.KeyedVectors.load_word2vec_format(d2v_path, binary=True)
