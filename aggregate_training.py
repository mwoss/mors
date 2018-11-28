import argparse
import logging.config
import os

from configuration.config import Config
from model.doc2vec.doc2vec_model import D2V
from model.lda.lda_model import LDA
from model.tfidf.tfidf_model import TFIDF
from preprocessing.parser import Parser
from preprocessing.preprocessor import Preprocessor
from search_engine.lda_engine import LdaEngine
from search_engine.tfidf_engine import TfidfEngine

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Search engine parameters')
    parser.add_argument('-a', '--algorithm', choices=['lda', 'doc2vec', 'tfidf'])
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    profile = args.config

    p_config = Config(profile=profile).preprocessor
    articles = []
    if p_config['source'] == 'crawl':
        articles = parse_articles(p_config['data_path'], p_config['encoding'])
    elif p_config['source'] == 'zips':
        articles = parse_articles_zip(p_config['data_path'], p_config['encoding'])

    algorithm = args.algorithm
    if algorithm == 'lda':
        logger.info("Chosen lda")
        config = Config(profile).lda
        lda = LDA.with_url_handling(
            config['max_workers'],
            config['topics'],
            config['passes']
        )

        if p_config['source'] == 'wiki':
            docs = preprocess_wiki(p_config['data_path'], p_config['max_workers'])
        else:
            docs = preprocess_doc(articles, p_config['max_workers'])

        lda.train([x[1] for x in docs])
        lda.save_model(config['model_path'])
        lda.save_model(config['dict_path'])

        lda_search_engine = LdaEngine(config['topics'], config['max_workers'])
        lda_search_engine.create_index(docs)
        lda_search_engine.save_index(config['index_path'], config['url_path'])
    elif algorithm == 'doc2vec':
        logger.info("chosen doc2vec")
        config = Config(profile).doc2vec
        trainer = D2V(config['max_workers'],
                      config['vector_size'],
                      config['window'],
                      config['min_count'],
                      config['epochs'],
                      config['dbow_model_path'] + 'model',
                      config['dm_model_path'] + "model")

        if p_config['source'] == 'wiki':
            docs = preprocess_tagged_wiki(p_config['data_path'])
        else:
            docs = preprocess_tagged_doc(articles, p_config['max_workers'])
        trainer.train(docs)
        trainer.save_models()


    elif algorithm == 'tfidf':
        logger.info("Chosen tfidf")
        config = Config(profile).tfidf
        tfidf = TFIDF.with_url_handling(
            config['max_workers']
        )
        if p_config['source'] == 'wiki':
            docs = preprocess_wiki(p_config['data_path'], p_config['max_workers'])
        else:
            docs = preprocess_doc(articles, p_config['max_workers'])

        tfidf.train([x[1] for x in docs])
        tfidf.save_model(config['model_path'])
        tfidf.save_dictionary(config['dict_path'])
        tfidf_engine = TfidfEngine(config['max_workers'])
        tfidf_engine.load_model(config['model_path'], config['dict_path'])
        tfidf_engine.create_index(docs)
        tfidf_engine.save_index(config['index_path'], config['url_path'])


def parse_articles(resource_path, encoding):
    data_directories = [os.path.join(resource_path, o) for o in os.listdir(resource_path) if
                        os.path.isdir(os.path.join(resource_path, o))]
    article_parser = Parser(data_directories, encoding)
    return article_parser.parse_articles_from_directories()


def parse_articles_zip(resource_path, encoding):
    data_directories = [os.path.join(resource_path, o) for o in os.listdir(resource_path) if
                        os.path.isdir(os.path.join(resource_path, o))]
    article_parser = Parser(data_directories, encoding)
    return article_parser.parse_reuters_data()


def preprocess_doc(articles, max_workers):
    preprocessor = Preprocessor(max_workers)
    return preprocessor.process_docs_with_urls(articles)


def preprocess_wiki(wiki, max_workers):
    logger.info("preprocessing {0}".format(wiki))
    preprocessor = Preprocessor(max_workers)
    return preprocessor.process_wiki(wiki)


def preprocess_tagged_wiki(wiki):
    preprocessor = Preprocessor(None)
    return preprocessor.preprocess_tagged_wiki(wiki)


def preprocess_tagged_doc(articles, max_workers):
    preprocessor = Preprocessor(max_workers)
    return preprocessor.preproces_tagged_docs_with_urls(articles)


if __name__ == "__main__":
    logging.config.fileConfig("configuration/logger.conf",
                              disable_existing_loggers=False)
    main()
