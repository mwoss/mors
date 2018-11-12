import logging
import sys

from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, LdaMulticore

from preprocessing.preprocessor import Preprocessor
from model.util.file_parser import parse_dir_json
from configuration.config import Config

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    config = Config(profile='local').lda

    _, docs = zip(*parse_dir_json(config['data_path']))

    preprocessed_docs = Preprocessor(max_workers=config['max_workers']).process_docs(docs)

    logger.info("Loading model from %s", config['model_path'])
    lda_model = LdaMulticore.load(config['model_path'])
    logger.info("Loading dictionary from %s", config['dict_path'])
    dictionary = Dictionary.load(config['dict_path'])

    coherence_model_lda = CoherenceModel(
        model=lda_model,
        texts=preprocessed_docs,
        dictionary=dictionary,
        coherence='c_v')

    coherence_lda = coherence_model_lda.get_coherence()

    import csv

    with open(config['coherence_path'], "a") as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow([config['topics'], coherence_lda])
