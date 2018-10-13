import logging

from gensim.models.doc2vec import Doc2Vec

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Trainer(object):
    def __init__(self, cores, vector_size, window, min_count, epochs, dbow_name,dm_name):
        self.cores = cores
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.dbow_name = dbow_name
        self.dm_name = dm_name
        logger.info("Cores used in training: {0}".format(self.cores))
        self.models = [
            # PV-DBOW
            Doc2Vec(dm=0, dbow_words=1, vector_size=self.vector_size, window=self.window, seed=42,
                    mmin_count=self.min_count, epochs=self.epochs, workers=self.cores),
            # PV-DM w/average
            Doc2Vec(dm=1, dm_mean=1, vector_size=self.vector_size, window=self.window, seed=42,
                    min_count=self.min_count, epochs=self.epochs, workers=self.cores),
        ]

    def build_vocabulary(self, preprocessed_docs):
        logger.info("building vocabulary")
        self.models[0].build_vocab(preprocessed_docs)
        print(str(self.models[0]))
        self.models[1].reset_from(self.models[0])
        print(str(self.models[1]))

    def train_model(self, preprocessed_docs):
        logger.info("training model")
        for m in self.models:
            m.train(preprocessed_docs, total_examples=m.corpus_count, epochs=m.epochs)
        self.models[0].save(self.dbow_name)
        self.models[1].save(self.dm_name)

    def train(self, preprocessed_docs):
        self.build_vocabulary(preprocessed_docs)
        self.train_model(preprocessed_docs)
        return self.models
