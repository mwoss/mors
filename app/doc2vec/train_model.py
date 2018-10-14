import logging

import argparse
import os
from configuration.doc2vec.config import Doc2VecConfig
from preprocessing.Preprocessor import Preprocessor
from preprocessing.Parser import Parser
from model.doc2vec.Training import Trainer

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Search engine parameters')
parser.add_argument('-p', '--profile', type=str, help='config profile')
args = parser.parse_args()

config = Doc2VecConfig(args.profile).get_configuration()

d = config['data_path']
data_directories = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]
article_parser = Parser(data_directories, config['encoding'])
articles = article_parser.parse_articles_from_directories()
preprocessor = Preprocessor(config['max_workers'])
docs = preprocessor.process_docs_with_urls(articles)
trainer = Trainer(config['max_workers'], config['vector_size'], config['window'], config['min_count'], config['epochs'],
                  config['dbow_model_path'] + 'model', config['dm_model_path'] + "model")
trainer.train(docs)


