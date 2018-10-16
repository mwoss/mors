from _yaml import YAMLError
from enum import Enum
from os.path import abspath

from yaml import load


class ConfigNotFoundException(Exception):
    def __init__(self, config_name):
        self.config_name = config_name
        super().__init__(f"Config {config_name} was not found in conf/ directory")


class ConfigProfileNotFoundException(Exception):
    def __init__(self, profile):
        self.profile = profile
        super().__init__(f"Config file didn't include profile: {profile}")


class ConfigLoader:
    @staticmethod
    def load(conf_path, config_name):
        file_path = abspath(f'{conf_path}{config_name}')
        try:
            with open(file_path, 'r') as yml_file:
                return load(yml_file)
        except FileNotFoundError:
            raise ConfigNotFoundException(config_name)


class Config:
    CONF_PATH = 'configuration_files/'

    def __init__(self, profile):
        self._profile = profile  # type: str

    def __getattr__(self, item):
        try:
            config_dict = self._get_config(item).get(self.profile)
            self.__dict__[item] = config_dict
            return config_dict
        except AttributeError:
            raise ConfigProfileNotFoundException(self._profile)

    def _get_config(self, item):
        config_name = f'{item}.yml'
        return ConfigLoader.load(self.CONF_PATH, config_name)
