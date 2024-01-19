import logging
import logging.config
import yaml


def initialize():
    with open("logging.yaml", "r") as stream:
        config = yaml.load(stream, Loader = yaml.FullLoader)
        logging.config.dictConfig(config)


initialize()
