import os
import json
import logging

__version__ = "0.1.0"

config = {"log_level": 30}

if os.getenv("TALKED_CONFIG_PATH"):
    with open(os.getenv("TALKED_CONFIG_PATH")) as config_file:
        try:
            custom_config = json.load(config_file)
        except ValueError:
            exit("Invalid json in config file.")
    config.update(custom_config)

logging.basicConfig(level=config["log_level"])
