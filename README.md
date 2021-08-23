# Talked

Call recording for Nextcloud Talk

## How it works

Talked works by launching a Firefox instance in a virtual framebuffer, joining the Talk call, and then recording whatever is on screen using FFmpeg. The call is in fullscreen and using the speaker view. During your call, the recording user will be visible while the recording is active. Some custom CSS is added to the page so, when recording in speaker view, the recording user is completely hidden from the recording itself.

## Hardware requirements

The default configuration has been designed to run on a 2 core / 2 GB ram VPS. If you have beefier hardware and would like better recording quality, then you can play around with the settings to increase the resolution, crf and encoding preset.

## Current limitations

These are the current limitations of Talked. They will be worked on for future releases.

* Only one recording can be active at a time.
* The HTTP API is design to be single threaded and only handle one request at a time.
* Recording only works with rooms that are public (Allows guest access through a link).
* The recording is set up to use speaker view, but if the recorder is started while a screen share is active and then the screen share is ended the recording will use grid view from that point on. This mainly means the recording user will be visible in the recording. The recording user is completely hidden from the recording when using speaker view.

## Installation

These instructions are made for Ubuntu 20.04, but they should hopefully be fairly easy to use for other distros, if you're familiar with them. These instructions are mainly intended to help you get started and should be adapted to your needs.

First let's install the required dependencies
```
sudo apt install build-essential python3 python3-dev python3-venv python3-wheel firefox-geckodriver pulseaudio xvfb ffmpeg
```

Then let's create an unprivileged user to run Talked with.
```
sudo useradd --system --shell /bin/bash --home-dir /opt/talked --create-home talked
```

Then change to the newly created user with `sudo su talked` as it will be easier to set up the virtual env. To set up the virtual env run the following
```
python3 -m venv /opt/talked/talked
```
Then activate it
```
source /opt/talked/talked/bin/activate
```
And install wheel and talked
```
pip3 install wheel talked
```

Now let's create the config file at `/opt/talked/config.json`. The only required parameter is `base_url` but it might be useful to change some of the other options as well. You can see a list of the available options further down. The most basic config would look like this:
```
{
    "base_url": "talked.example.com"
}
```

Talked uses the environment variable `TALKED_CONFIG_PATH` to find the config file. The easiest way to set it is to put it in the systemd service file used to start the talked server.

Further down you can find an example systemd unit file that can be used to start and stop the Talked server. You can use the following command to test the Talked server. Please note the command binds to localhost, you can change it to whatever you need.
```
uwsgi --http 127.0.0.1:5000 --master --manage-script-name --mount /=talked.main:app
```

It's recommended to set up Nginx or Apache in front of uwsgi to handle TLS and HTTP Basic auth. Currently, there isn't any authentication system built into the Talked server, so it's recommend to set up HTTP Basic auth. It's also recommended to only allow requests from your Nextcloud server to the Talked server, this can either be configured in your firewall or web server config.

You can have a look at the following instructions for nginx: https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/

## Configuration options

| option                  | default    | description                                                                                         |
| ----------------------- | ---------- | --------------------------------------------------------------------------------------------------- |
| base_url                | ""         | The base URL of your Nextcloud instance. Should include the http / https and have no leading slash. |
| log_level               | "warning"  | The log level that should be used.                                                                  |
| recording_dir           | "."        | The directory where the recordings should be stored.                                                |
| video_width             | 1280       | The virtual display and recording width in pixels.                                                  |
| video_height            | 720        | The virtual display and recording height in pixels.                                                 |
| color_depth             | 24         | The color depth to use for the virtual framebuffer.                                                 |
| framerate               | 30         | The framerate that should be used for the recording.                                                |
| audio_codec             | "aac"      | The audio codec to use for the recording.                                                           |
| audio_bitrate           | "160k"     | The audio bitrate to use.                                                                           |
| audio_thread_queue_size | 128        |                                                                                                     |
| video_codec             | "libx264"  | The video codec to use for the recording.                                                           |
| crf                     | 25         | The crf to use for the H.264 encoding.                                                              |
| video_thread_queue_size | 32         |                                                                                                     |
| encoding_preset         | "veryfast" | The encoding preset used for the H.264 encoding.                                                    |
| encoding_threads        | 0          | How many threads to use for the encoding. 0 is auto.                                                |

## Development setup

Make sure you have docker installed for your OS. Then build the generic docker container using this command
```
docker build docker -f docker/Dockerfile.dev -t talked
```

Then start the container using this command, it will take over the current terminal you have open. The command will start the docker container giving you a bash shell and a user with the same ID as your user on the host. The root of this project will also be passed through to the container in the /home/talked/talked folder. The container will get removed when you exit out of it, so you don't manually have to do it.
```
docker run --rm -it -v "$(pwd):/home/talked/talked" -e "UID=$(id -u)" -e "GID=$(id -g)" -p "5000:5000" talked
```

When you enter the container you will be placed in the /home/talked/talked folder, to get started first install the python dependencies using poetry.
```
poetry install
```

Then create a config file called `config.json` in the root of the project which contains the base URL for your Nextcloud instance. Below you can see the boilerplate:
```
{
  "base_url": "https://nextcloud.example.com"
}
```
The config file location is controlled by the `TALKED_CONFIG_PATH` env var and by default, in the container, it is set to the root of the project folder.

Now you can run the program either using:
```
poetry run python3 -m talked
```
Or by entering the virtualenv and then running the program:
```
poetry shell

python3 -m talked
```

Lastly remember to join the call before starting the program, as it will only join if there is a call in progress.

## Example systemd service

```
[Unit]
Description=talked
Requires=network.target
After=network.target

[Service]
WorkingDirectory=/opt/talked
User=talked
Group=talked

Environment=TALKED_CONFIG_PATH=/opt/talked/config.json

ProtectSystem=full
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
PrivateTmp=yes
NoNewPrivileges=yes

SyslogIdentifier=talked
StandardOutput=syslog
StandardError=syslog

ExecStart=/opt/talked/talked/bin/uwsgi --http 127.0.0.1:5000 --die-on-term --master --manage-script-name --mount /=talked.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

This program is licensed under the AGPLv3 or later.
