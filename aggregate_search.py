import logging.config
from search_engine.engine.engines.lda_engine import LdaEngine
from search_engine.engine.engines.tfidf_engine import TfidfEngine
from search_engine.engine.engines.d2v_engine import D2VEngine


class AggregateSearch(object):

    def __init__(self, *engines):
        self.engines = engines

    def search(self, query):
        dict_results = [engine.dict_search(query, results=50) for engine in self.engines]
        results = dict_results[0].keys()

        weighted_results = [(url, self.weighted_res(url, dict_results)) for url in results]
        return sorted(weighted_results, key=lambda x: -x[1])

    def weighted_res(self, url, dict_results):
        return sum([res[url] for res in dict_results if url in res]) / len(self.engines)


if __name__ == '__main__':
    logging.config.fileConfig("configuration/logger.conf", disable_existing_loggers=False)

    search = AggregateSearch(LdaEngine.from_configfile(), TfidfEngine.from_configfile(),
                             D2VEngine.from_configfile())

    inp = ""

    while inp != 'q':
        inp = input("Enter query: ")
        print(search.search(inp)[:3])
