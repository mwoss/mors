import sys

from configuration.tfidf.config import TfidfConfig
from model.tfidf.logger.logger_config import init_logger
from model.tfidf.tfidf_model import TFIDF
from model.util.file_parser import parse_dir_json

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
