import logging

import os
from singleton_decorator import singleton
import yaml

logger = logging.getLogger(__name__)


class InvalidConfigException(Exception):
    pass


@singleton
class LdaConfig(object):
    def __init__(self, profile):
        self.profile = profile
        self.current_config = None

    def get_current_config(self):
        cfg = None
        with open("configuration/lda/config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        if cfg is not None:
            logger.info("Successfully loaded configuration")
            return cfg[self.profile]

        if self.current_config is not None:
            logger.warning("Failed to load new configuration. returning last valid lda")
            return self.current_config
        else:
            raise InvalidConfigException("Could not load new lda. No existing lda available either")
