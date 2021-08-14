import os
import json
import logging
import sys

__version__ = "0.1.1"

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

config = {
    "log_level": "warning",
    "video_width": 1280,
    "video_height": 720,
    "color_depth": 24,
    "framerate": 30,
    "video_thread_queue_size": 1024,
    "audio_thread_queue_size": 1024,
    "crf": 25,
    "encoding_preset": "veryfast",
    "encoding_threads": 0,
}

if os.getenv("TALKED_CONFIG_PATH"):
    with open(os.getenv("TALKED_CONFIG_PATH")) as config_file:
        try:
            custom_config = json.load(config_file)
        except ValueError:
            exit("Invalid json in config file.")
    config.update(custom_config)

logging.basicConfig(level=LOG_LEVELS[config["log_level"]])

if not config.get("base_url"):
    logging.critical("base_url is required!")
    sys.exit()
