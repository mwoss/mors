import logging
from concurrent.futures import ProcessPoolExecutor

from gensim.models.doc2vec import TaggedDocument
from nltk import PorterStemmer, RegexpTokenizer
from stop_words import get_stop_words

logger = logging.getLogger(__name__)


class Preprocessor:
    def __init__(self, max_workers):
        logger.info("Number of workers: %s", max_workers)
        self.max_workers = max_workers
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.en_stopwords = set(get_stop_words('en'))
        self.p_stemmer = PorterStemmer()

    def preprocess_doc(self, doc):
        tokens = self.tokenizer.tokenize(doc.lower())
        stopped_tokens = [i for i in tokens if i not in self.en_stopwords]
        stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]
        return stemmed_tokens

    def preprocess_doc_with_url(self, doc_with_url):
        url, content = doc_with_url
        logger.info("preprocess_doc_with_url with url: %s", url)
        return url, self.preprocess_doc(content)

    def preprocess_tagged_doc_with_url(self, doc_with_url):
        url, preprocessed_doc = self.preprocess_doc_with_url(doc_with_url)
        return TaggedDocument(preprocessed_doc, tags=[url])

    def process_docs(self, doc_list):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.preprocess_doc, doc_list))

    def process_docs_with_urls(self, urldoc_list):
        logger.info("Process docs with urls ")
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.preprocess_doc_with_url, urldoc_list))

    def preproces_tagged_docs_with_urls(self, tagged_url_doc_list):
        logger.info("Process tagged docs")
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.preprocess_tagged_doc_with_url, tagged_url_doc_list))

    def preprocess_query(self, doc):
        tokens = self.tokenizer.tokenize(doc.lower())
        stopped_tokens = [i for i in tokens if i not in self.en_stopwords]
        stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]
        return stemmed_tokens


class WithUrlPreprocessor(Preprocessor):
    def __init__(self, max_workers=4):
        super().__init__(max_workers=max_workers)

    def preprocess_doc(self, doc):
        _, content = doc
        return super().preprocess_doc(content)
