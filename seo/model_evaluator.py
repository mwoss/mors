import itertools

import gensim
import numpy as np
from gensim.parsing.preprocessing import STOPWORDS
import random
from gensim.utils import smart_open, simple_preprocess

from logging import getLogger
import csv
from os import environ
from gensim.corpora.wikicorpus import _extract_pages, filter_wiki

import requests
import time

from configuration.config import Config
from seo.abstract_evaluator import AbstractEvaluator

logger = getLogger(__name__)


class WordIntrusion(AbstractEvaluator):
    def __init__(self, max_workers, topics):
        super().__init__(max_workers, topics)

    @classmethod
    def from_configfile(cls):
        return super(WordIntrusion, cls).from_configfile()

    def get_words(self, num_topics=15, num_words_per_topics=6):
        to_display = [
            [word for word, _ in self.model.show_topic(topicno, topn=num_words_per_topics)]
            for topicno
            in range(num_topics)]
        flatten = lambda l: [item for sublist in l for item in sublist]

        to_insert = random.sample(flatten([
            [word for word,_ in self.model.show_topic(topicno, topn=num_words_per_topics)]
            for topicno
            in range(num_topics, num_topics*2)]
        ), num_topics)
        def concat_shuffle(array,item):
            result = array + [item]
            random.shuffle(result)
            return result
        return [
            concat_shuffle(words,inser_word) + [inser_word] for words, inser_word in zip(to_display, to_insert)
        ]

    # def get_mixed_topics(self):


def load_wiki(wiki_path):
    """
       method taken  from https://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
    """
    # evaluate on 1k documents **not** used in LDA training
    doc_stream = (tokens for _, tokens in iter_wiki(wiki_path))  # generator
    return list(itertools.islice(doc_stream, 0, 1000))


def tokenize(text):
    """
    method taken  from https://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
    """
    return [token for token in simple_preprocess(text) if token not in STOPWORDS]


class Sample(object):

    def __init__(self, correct_words, wrong_word):
        self.correct_words = correct_words,
        self.wrong_word = wrong_word

    def get_mixed_topics(self):
        return random.shuffle(self.correct_words + [self.wrong_word])


def iter_wiki(dump_file):
    """
    method taken  from https://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
    Yield each article from the Wikipedia dump, as a `(title, tokens)` 2-tuple."""
    ignore_namespaces = 'Wikipedia Category File Portal Template MediaWiki User Help Book Draft'.split()
    for title, text, pageid in _extract_pages(smart_open(dump_file)):
        text = filter_wiki(text)
        tokens = tokenize(text)
        if len(tokens) < 50 or any(title.startswith(ns + ':') for ns in ignore_namespaces):
            continue  # ignore short articles and various meta-articles
        yield title, tokens


def parse_categories(categories_path):
    with open(categories_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        return [row for row in csv_reader]


def get_query_resut(phrase):
    try:
        params = {'q': phrase,
                  'format': 'json'}
        response = requests.get('https://api.duckduckgo.com', params=params)
        response_json = response.json()
        time.sleep(0.05)
        return response_json['AbstractURL'], response_json['AbstractText']
    except:
        return "", ""


def get_query_result_with_retry(phrase, retry_max=5):
    def incorrect_result(query_result):
        return not query_result[0] or not query_result[1]

    query_result = ("", "")
    retry_curr = 0

    while incorrect_result(query_result) and retry_curr < retry_max:
        query_result = get_query_resut(phrase)
        retry_curr += 1

    logger.info('attempts to download from DDG API: {}'.format(retry_curr))

    return False if incorrect_result(query_result) else query_result


class CategoriesEvaluator(AbstractEvaluator):

    def __init__(self, max_workers, topics, categories):
        super().__init__(max_workers, topics)
        self.categories = categories

    def get_random_query_results(self, category, number):

        new_categories = list(self.categories)
        new_categories.remove(category)
        cat_to_go = random.sample(new_categories, number)
        result = []
        for category in cat_to_go:

            query_res = get_query_result_with_retry(random.choice(category))
            if query_res:
                result.append(query_res)

        return result

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        categories_evaluator = cls(lda_config['max_workers'], lda_config['topics'],
                                   parse_categories(lda_config['categories_path']))
        categories_evaluator.load_model(lda_config['model_path'], lda_config['dict_path'])
        return categories_evaluator

    def testCategories(self, passes=3, phrases_per_topic=10, false_queries=2):
        """
        The idea is to use DuckDuckGo API as a black box and compare our model's results against it.
        We take a phrase from category, let's say our phrase is 'bussiness intelligence' from
        category 'Bussiness'. Then we take false_queries number of other phrases from different topics,
        for example 'best artist in 2018' from 'Art' and 'cheap Real Estate' from 'Real estate'
        Then we get the results for these query from the API and compare whether,
        according to our model, the similarity between 'bussiness inteligence' and its
        result from API is higher than similarities with 'false'queries.

        :param passes: How many times you want an algorithm to be performed.
                       Algorithm covers only little space of all possible combinations.
                       The choice is made by random so you may want to run it multiple times
        :param phrases_per_topic: how many phrases per topic you want to use in single run( for each pass)
        :param false_queries: how many false categories you want to choose.
                Example: you have a phrase from category 'finance'.
                if false_queries is set to 2, algorithm will take also phrases
                from 2 other categories and then compare similarities with phrase
                against them and the correct category
        :return: list of results. single result can be one of {0,1} and model's score
                    1 : proper result is most similar to the query
                    0 : if not

        """
        results = []
        for i in range(passes):
            for category in self.categories:
                for phrase in random.sample([p for p in category if p], phrases_per_topic):
                    orininal_phrase = get_query_result_with_retry(phrase)
                    if orininal_phrase:
                        queries = self.get_random_query_results(category, false_queries)
                        queries.append(orininal_phrase)
                        sorted_queries = sorted(queries,
                                                key=lambda url_and_text:
                                                self.compute_similarity(url_and_text[1], phrase),
                                                reverse=True)

                        print(len(sorted_queries))
                        res_ind = sorted_queries.index(orininal_phrase)
                        if res_ind > 0:
                            print("phrase {} equivalent has index {} in \n {}".format(phrase, res_ind, sorted_queries))
                        results.append(1 if res_ind == 0 else 0)
        return results, sum(results) / len(results)


class IntraInterEvaluator(AbstractEvaluator):
    def __init__(self, max_workers, topics, wiki_docs):
        super().__init__(max_workers, topics)
        self.wiki_docs = wiki_docs
        self.part1, self.part2 = None, None

    @classmethod
    def from_configfile(cls):
        profile = environ.get('lda_profile', 'local')
        lda_config = Config(profile=profile).lda

        intra_inter_evaluator = cls(lda_config['max_workers'], lda_config['topics'],
                                    load_wiki(lda_config['wiki_path']))
        intra_inter_evaluator.load_model(lda_config['model_path'], lda_config['dict_path'])
        intra_inter_evaluator.split_wiki()

        return intra_inter_evaluator

    def split_wiki(self):
        # self.part1 = [self.model[self.m_dict.doc2bow(tokens[: len(tokens) // 2])] for tokens in self.wiki_docs]
        self.part1 = [self.model[self.m_dict.doc2bow(tokens[1::2])] for tokens in self.wiki_docs]
        self.part2 = [self.model[self.m_dict.doc2bow(tokens[0::2])] for tokens in self.wiki_docs]
        # self.part2 = [self.model[self.m_dict.doc2bow(tokens[len(tokens) // 2:])] for tokens in self.wiki_docs]

    def inter(self, pairs=10000):
        """
        Computes similarities between halves of different document.
        Generally "the smaller the better" however the reachable minimum depends on the data.
        Apply 2 rules when evaluating:
        1. This value should be generally smaller than the value from intra()
        2. Compare the absolute values only on the same wiki_date between 2 different models
        """
        random_pairs = np.random.randint(0, len(self.wiki_docs), size=(pairs, 2))
        distances = [gensim.matutils.cossim(self.part1[i[0]], self.part2[i[1]]) for i in random_pairs]

        return np.mean(distances), np.std(distances)

    def intra(self):
        """
        Computes similarities between halves of the same document.
        Generally, "the bigger the better", however the reachable maximum depends on the data.
        Apply 2 rules when evaluating:
        1. Return value should be generally higher than inter()
        2. Compare the absolute values only on the same wiki_date between 2 different models
        """
        distances = [gensim.matutils.cossim(p1, p2) for p1, p2 in zip(self.part1, self.part2)]
        return np.mean(distances), np.std(distances)
