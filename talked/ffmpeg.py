import os
import time
import logging
from talked import config

# Dict containing specific ffmpeg parameters
# and related options for each supported video codec
video_codecs = {
    "x264": {
        "args": [
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            str(config["crf"]),
            "-preset",
            config["encoding_preset"],
        ],
        "audio_codec": "aac",
        "file_extension": "mp4",
    },
}

# Dict containing specific ffmpeg parameters
# and related options for each supported audio codec
audio_codecs = {
    "aac": {
        "args": [
            "-c:a",
            "aac",
            "-b:a",
            config.get("audio_aac_bitrate", config["audio_bitrate"]),
        ],
        "file_extension": "aac",
    },
    "mp3": {
        "args": [
            "-c:a",
            "libmp3lame",
            "-b:a",
            config.get("audio_mp3_bitrate", config["audio_bitrate"]),
        ],
        "file_extension": "mp3",
    },
    "opus": {
        "args": [
            "-c:a",
            "libopus",
            "-b:a",
            config.get("audio_opus_bitrate", config["audio_bitrate"]),
        ],
        "file_extension": "opus",
    },
    "flac": {
        "args": [
            "-c:a",
            "flac",
        ],
        "file_extension": "flac",
    },
    "wave": {
        "args": [],
        "file_extension": "wav",
    },
}

# The base ffmpeg parameters, these parameters will always be used.
ffmpeg_base = [
    "ffmpeg",
    "-nostdin",
    "-nostats",
    "-hide_banner",
    "-loglevel",
    "warning",
    "-fflags",
    "+igndts",
]

# The ffmpeg parameters controlling the video input
ffmpeg_video_input = [
    "-f",
    "x11grab",
    "-video_size",
    f"{config['video_width']}x{config['video_height']}",
    "-framerate",
    str(config["framerate"]),
    "-draw_mouse",
    "0",
    "-thread_queue_size",
    str(config["video_thread_queue_size"]),
    "-i",
]

# The ffmpeg parameters controlling the audio input
ffmpeg_audio_input = [
    "-f",
    "pulse",
    "-ac",
    "2",
    "-channel_layout",
    "stereo",
    "-thread_queue_size",
    str(config["audio_thread_queue_size"]),
    "-i",
    "0",
]


def assemble_command(audio_only: bool):
    if audio_only:
        try:
            audio_codec = audio_codecs[config["audio_codec"]]
        except KeyError:
            logging.critical("The chosen audio codec isn't supported")
            raise RuntimeError

        file_extension = audio_codec["file_extension"]
    else:
        try:
            video_codec = video_codecs[config["video_codec"]]
        except KeyError:
            logging.critical("The chosen video codec isn't supported")
            raise RuntimeError

        audio_codec = audio_codecs[video_codec["audio_codec"]]
        file_extension = video_codec["file_extension"]

    command = ffmpeg_base + ffmpeg_audio_input

    if not audio_only:
        command += ffmpeg_video_input
        command += [os.environ["DISPLAY"]]
        command += video_codec["args"]

    command += audio_codec["args"]

    command += [
        "-threads",
        str(config["encoding_threads"]),
        (
            f"{config['recording_dir']}/"
            f"{time.strftime('%Y%m%dT%H%M%S')}_output.{file_extension}"
        ),
    ]

    return command
