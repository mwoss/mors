import logging

from gensim.models.doc2vec import Doc2Vec

logger = logging.getLogger(__name__)


class D2V(object):
    def __init__(self, cores, vector_size, window, min_count, epochs, dbow_name, dm_name):
        self.cores = cores
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.dbow_name = dbow_name
        self.dm_name = dm_name
        logger.info("Workers used in training: %s", self.cores)
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

    def train_models(self, preprocessed_docs):
        logger.info("Training models")
        for m in self.models:
            m.train(preprocessed_docs, total_examples=m.corpus_count, epochs=m.epochs)

    def save_models(self):
        logger.info("Saving models")
        self.models[0].save(self.dbow_name)
        self.models[1].save(self.dm_name)

    def train(self, preprocessed_docs):
        self.build_vocabulary(preprocessed_docs)
        self.train_models(preprocessed_docs)
        return self.models
