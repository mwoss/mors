from pickle import dump, load


def save_model(filename, savable_data):
    with open(filename, 'wb') as file:
        dump(savable_data, file)


def load_model(filename):
    with open(filename, 'rb') as file:
        return load(file)


class EmptyObjectAttrException(Exception):
    def __init__(self):
        super().__init__("Load model/index before making any operation on search engine")


class EmptyObject:
    def __setattr__(self, key, value):
        raise EmptyObjectAttrException

    def __getattr__(self, item):
        raise EmptyObjectAttrException


class EmptyModel(EmptyObject):
    def __len__(self):
        raise EmptyObjectAttrException


class EmptyIndex(EmptyObject):
    pass

# TODO: implement base interface for lda, tfidf, d2v models, Aniu :33
#  open for new attrs, extra __call__  method modification etc, dunno if we should differ empty index and empty model
