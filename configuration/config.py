from os.path import abspath

from yaml import load


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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


class Config(metaclass=Singleton):
    CONF_PATH = 'configuration_files/'

    def __init__(self, profile):
        self._profile = profile  # type: str

    def __getattr__(self, item):
        try:
            config_dict = self._get_config(item)
            self.__dict__[item] = config_dict.get(self._profile)
            return config_dict
        except AttributeError:
            raise ConfigProfileNotFoundException(self._profile)

    def _get_config(self, item):
        config_name = f'{item}.yml'
        return ConfigLoader.load(self.CONF_PATH, config_name)
