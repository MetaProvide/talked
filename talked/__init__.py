import json
import logging
import os
import sys

from tomlkit import parse

__version__ = "0.3.0"

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

config = {
    "log_level": "warning",
    "recording_dir": ".",
    "grid_view": False,
    "video_width": 1280,
    "video_height": 720,
    "color_depth": 24,
    "framerate": 30,
    "audio_only": False,
    "audio_codec": "wave",
    "audio_bitrate": "160k",
    "audio_thread_queue_size": 128,
    "video_codec": "x264",
    "crf": 25,
    "video_thread_queue_size": 32,
    "encoding_preset": "veryfast",
    "encoding_threads": 0,
}

if os.getenv("TALKED_CONFIG_PATH"):
    with open(os.getenv("TALKED_CONFIG_PATH"), encoding="utf-8") as config_file:
        if os.path.splitext(os.getenv("TALKED_CONFIG_PATH"))[1] == ".toml":
            try:
                custom_config = parse(config_file.read())
            except ValueError:
                logging.critical("Invalid toml in config file.")
                sys.exit()
        elif os.path.splitext(os.getenv("TALKED_CONFIG_PATH"))[1] == ".json":
            try:
                custom_config = json.load(config_file)
            except ValueError:
                logging.critical("Invalid json in config file.")
                sys.exit()
            logging.warning("DEPRECATED: Please switch to a toml config file")
        else:
            logging.critical("Please provide a toml config file!")
            sys.exit()

    config.update(custom_config)

logging.basicConfig(level=LOG_LEVELS[config["log_level"]])

if not config.get("base_url"):
    logging.critical("base_url is required! Please specify it in the config file.")
    sys.exit()

if not os.path.isdir(config["recording_dir"]):
    logging.critical(
        "The specified recording directory doesn't exist, please create it!"
    )
    sys.exit()
