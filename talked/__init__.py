import json
import logging
from talked import recorder


def main():
    with open("config.json") as config_file:
        try:
            config = json.load(config_file)
        except ValueError:
            exit("Invalid json in config file.")

    logging.basicConfig(level=config["log_level"])

    recorder.start(config)


if __name__ == "__main__":
    main()
