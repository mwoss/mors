import sys

from model.util.file_parser import parse_dir_json
from search_engine.lda.search_engine import LdaEngine
from search_engine.lda.logger.logger_config import init_logger
from configuration.lda.config import LdaConfig

if __name__ == '__main__':
    init_logger()

    config = LdaConfig(sys.argv[1], 'lda_search_engine').get_current_config()

    docs = parse_dir_json(config['data_path'])

    searchEngine = LdaEngine(config['topics'])
    searchEngine.load_model(config['model_path'], config['dict_path'])
    searchEngine.create_index(docs)

    searchEngine.save_index(config['index_path'], config['url_path'])
    searchEngine.load_index(config['index_path'], config['url_path'])

    inp = ""

    while inp != 'q':
        inp = input("Enter query: ")
        print(searchEngine.search(inp)[:3])
