from enum import Enum
from os.path import abspath

from yaml import load


class ConfigNotFoundException(Exception):
    def __init__(self, path, config):
        self.config = config
        self.path = path
        super().__init__(f"Config {config} was not found in conf/ directory")


class Prefix(Enum):
    NO_PREFIX = ''
    LOCAL = 'local_'
    PRODUCTION = 'prod_'


class ConfigLoader:
    @staticmethod
    def load(conf_path, config_name):
        file_path = abspath(f'{conf_path}{config_name}')
        try:
            with open(file_path, 'r') as yml_file:
                return load(yml_file)
        except FileNotFoundError:
            raise ConfigNotFoundException(file_path, config_name)


class Config:
    CONF_PATH = 'configuration_files/'

    def __init__(self, file_prefix):
        self._file_prefix = file_prefix  # type: Prefix

    def __getattr__(self, item):
        config_dict = self._get_config(item)
        self.__dict__[item] = config_dict
        return config_dict

    def _get_config(self, item):
        config_name = f'{self._file_prefix.value}{item}.yml'
        return ConfigLoader.load(self.CONF_PATH, config_name)
