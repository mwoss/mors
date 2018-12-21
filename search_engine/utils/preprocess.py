from concurrent.futures import ProcessPoolExecutor

from nltk import PorterStemmer, RegexpTokenizer
from stop_words import get_stop_words


class Preprocessor(object):
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.en_stopwords = set(get_stop_words('en'))
        self.p_stemmer = PorterStemmer()

    def preprocess_doc(self, doc):
        tokens = self.tokenizer.tokenize(doc.lower())

        stopped_tokens = [i for i in tokens if i not in self.en_stopwords]

        stemmed_tokens = [self.p_stemmer.stem(i) for i in stopped_tokens]

        return stemmed_tokens

    def process_docs(self, doc_list):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            return [self.preprocess_doc(doc) for doc in doc_list]

    def preprocess_doc_with_url(self, doc_with_url):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            url, content = doc_with_url

        return url, self.preprocess_doc(content)

    def process_docs_with_urls(self, urldoc_list):
        return [self.preprocess_doc_with_url(urldoc) for urldoc in urldoc_list]


class WithUrlPreprocessor(Preprocessor):
    def __init__(self, max_workers=4):
        super().__init__(max_workers=max_workers)

    def preprocess_doc(self, doc):
        _, content = doc
        return super().preprocess_doc(content)
