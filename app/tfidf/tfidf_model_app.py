import sys

from search_engine.configuration import TfidfConfig
from search_engine.model import init_logger
from search_engine.model import TFIDF
from search_engine.model import parse_dir_json

if __name__ == '__main__':
    init_logger()

    config = TfidfConfig(sys.argv[1]).get_current_config()

    docs = parse_dir_json(config['data_path'])

    tfidf = TFIDF.with_url_handling(
        config['max_workers']
    )

    tfidf.train(docs)
    tfidf.save_model(config['model_path'])
    tfidf.save_dictionary(config['dict_path'])
