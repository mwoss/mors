import sys

from search_engine.model import LDA
from search_engine.model import parse_dir_json
from search_engine.configuration import LdaConfig
from search_engine.model import init_logger

if __name__ == '__main__':
    init_logger()

    config = LdaConfig(sys.argv[1]).get_current_config()

    docs = parse_dir_json(config['data_path'])

    lda = LDA.with_url_handling(
        config['max_workers'],
        config['topics'],
        config['passes']
    )

    lda.train(docs)
    lda.save_model(config['model_path'])
    lda.save_dictionary(config['dict_path'])
