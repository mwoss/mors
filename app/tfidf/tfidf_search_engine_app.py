import sys

from search_engine.configuration import TfidfConfig
from search_engine.model import parse_dir_json
from search_engine.engine import TfidfEngine
from search_engine.engine import init_logger

if __name__ == '__main__':
    init_logger()

    config = TfidfConfig(sys.argv[1], 'tfidf_search_engine').get_current_config()

    docs = parse_dir_json(config['data_path'])

    searchEngine = TfidfEngine()
    searchEngine.load_model(config['model_path'], config['dict_path'])
    searchEngine.dummy_index(docs)

    searchEngine.save_index(config['index_path'], config['url_path'])

    print(searchEngine.search("israel bank money")[:3])
    print(searchEngine.search("biggest wars in europe history")[:3])

    print(searchEngine.search("bitcoin and blockchain are future")[:3])

    print(searchEngine.search("gay marriages in europe")[:3])

    print(searchEngine.search("USA trump foreign policy")[:3])

    inp = ""

    while inp != 'q':
        inp = input("Enter query: ")
        print(searchEngine.search(inp)[:3])
