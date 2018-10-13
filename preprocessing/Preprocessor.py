from concurrent.futures import ProcessPoolExecutor

from stop_words import get_stop_words

from gensim.models.doc2vec import TaggedDocument

from nltk import PorterStemmer, RegexpTokenizer

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Preprocessor:

    def __init__(self, max_workers):
        logger.info("Number of workers: {0}".format(max_workers))
        self.max_workers = max_workers
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.en_stopwords = set(get_stop_words('en'))
        self.p_stemmer = PorterStemmer()

    def preprocess_doc_with_url(self, doc_with_url):
        url, content = doc_with_url
        logger.info("preprocess_doc_with_url with url: {0}".format(url))

        return TaggedDocument(self.preprocess_doc(content), tags=[url])

    def preprocess_doc(self, doc):
        tokens = self.tokenizer.tokenize(doc.lower())
        stopped_tokens = [i for i in tokens if i not in self.en_stopwords]
        stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]
        return stemmed_tokens

    def process_docs(self, doc_list):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.preprocess_doc, doc_list))

    def process_docs_with_urls(self, urldoc_list):
        logger.info("process docs with urls ")
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.preprocess_doc_with_url, urldoc_list))

    def preprocess_query(self, doc):
        tokens = self.tokenizer.tokenize(doc.lower())
        stopped_tokens = [i for i in tokens if i not in self.en_stopwords]
        stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]
        return stemmed_tokens
