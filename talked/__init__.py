import json
import logging

__version__ = "0.1.0"

with open("config.json") as config_file:
    try:
        config = json.load(config_file)
    except ValueError:
        exit("Invalid json in config file.")

logging.basicConfig(level=config["log_level"])
