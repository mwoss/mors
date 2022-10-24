from errno import EEXIST
from os import makedirs, path


def directory_check(directory):
    if not path.exists(path.dirname(directory)):
        try:
            makedirs(path.dirname(directory))
        except OSError as e:
            if e.errno != EEXIST:
                raise
