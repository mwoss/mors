import logging
from concurrent.futures import ProcessPoolExecutor
from gensim.corpora.wikicorpus import _extract_pages, filter_wiki

from gensim.models.doc2vec import TaggedDocument
from nltk import PorterStemmer, RegexpTokenizer
from smart_open import smart_open
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

    def iter_wiki(self, dump_file):
        logger.info("preprocessing dump {0}".format(dump_file))
        """Yield each article from the Wikipedia dump, as a `(title, tokens)` 2-tuple."""
        ignore_namespaces = 'Wikipedia Category File Portal Template MediaWiki User Help Book Draft'.split()
        index = 0
        for title, text, pageid in _extract_pages(smart_open(dump_file)):
            if index > 160_000:
                break
            text = filter_wiki(text)
            tokens = self.preprocess_doc(text)
            if len(tokens) < 50 or any(title.startswith(ns + ':') for ns in ignore_namespaces):
                continue  # ignore short articles and various meta-articles
            index += 1
            yield title, tokens

    def process_wiki(self, wiki):
        doc_stream = ((title, tokens) for title, tokens in self.iter_wiki(wiki))
        return list(doc_stream)

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

    def preprocess_tagged_wiki(self, wiki_path):
        logger.info("Creating tagged document from wiki corpus")
        tagged_wiki = []
        for title, tokens in self.iter_wiki(wiki_path):
            tagged_wiki.append(TaggedDocument(tokens, tags=[title]))
        return tagged_wiki

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
