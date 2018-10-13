import logging
from singleton_decorator import singleton

import yaml

logger = logging.getLogger(__name__)


class InvalidConfigException(Exception):
    pass


@singleton
class Doc2VecConfig(object):

    def __init__(self, profile):
        self.profile = profile
        self.current_config = None

    def get_configuration(self):
        cfg = None
        with open('configuration/doc2vec/config.yml') as ymlfile:
            cfg = yaml.load(ymlfile)
        if cfg is not None:
            logger.info("Successfully loaded configuration")
            return cfg[self.profile]
        if self.current_config is not None:
            logger.warning("Failed to load new configuration, returning last valid doc2vec configuration")
            return self.current_config
        else:
            logger.error("Could not load configuration")
            raise InvalidConfigException(
                "Could not load new model configuration. No existing model configuration available either")
