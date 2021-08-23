import os
import json
import logging
import sys

__version__ = "0.1.4"

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
    "video_width": 1280,
    "video_height": 720,
    "color_depth": 24,
    "framerate": 30,
    "audio_codec": "aac",
    "audio_bitrate": "160k",
    "audio_thread_queue_size": 128,
    "video_codec": "libx264",
    "crf": 25,
    "video_thread_queue_size": 32,
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
    logging.critical("base_url is required! Please specify it in the config file.")
    sys.exit()

if not os.path.isdir(config["recording_dir"]):
    logging.critical(
        "The specified recording directory doesn't exist, please create it!"
    )
    sys.exit()
