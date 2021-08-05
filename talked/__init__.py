import json
from talked import recorder


def main():
    with open("config.json") as config_file:
        try:
            config = json.load(config_file)
        except ValueError:
            exit("Invalid json in config file.")

    recorder.start(config)


if __name__ == "__main__":
    main()
