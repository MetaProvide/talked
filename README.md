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
And install talked and uwsgi
```
pip3 install talked wheel uwsgi
```

Now let's create the config file at `/opt/talked/config.toml`. The only required parameter is `base_url` but it might be useful to change some of the other options as well. You can see a list of the available options further down. The most basic config would look like this:
```
base_url = "talked.example.com"
```

Talked uses the environment variable `TALKED_CONFIG_PATH` to find the config file. The easiest way to set it is to put it in the systemd service file used to start the talked server.

Further down you can find an example systemd unit file that can be used to start and stop the Talked server. You can use the following command to test the Talked server. Please note the command binds to localhost, you can change it to whatever you need.
```
uwsgi --http 127.0.0.1:5000 --master --manage-script-name --mount /=talked.main:app
```

It's recommended to set up Nginx or Apache in front of uwsgi to handle TLS and HTTP Basic auth. Currently, there isn't any authentication system built into the Talked server, so it's recommend to set up HTTP Basic auth. It's also recommended to only allow requests from your Nextcloud server to the Talked server, this can either be configured in your firewall or web server config.

When using uwsgi behind a webserver it's recommended to use the `--http-socket` option instead to connect over a unix socket. To do so create the folder `/var/run/talked` with the appropriate permissions for your setup and then run talked using a command like below:
```
uwsgi --http-socket /var/run/talked/talked.sock --master --manage-script-name --mount /=talked.main:app
```

You can have a look at the following instructions for nginx: https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/

## Configuration options

| option                  | default    | description                                                                                                                                                                                                        |
| ----------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| base_url                | ""         | The base URL of your Nextcloud instance. Should include the http / https and have no leading slash.                                                                                                                |
| log_level               | "warning"  | The log level that should be used.                                                                                                                                                                                 |
| recording_dir           | "."        | The directory where the recordings should be stored.                                                                                                                                                               |
| grid_view               | false      | If set to true the recording uses grid view instead of speaker view. The recording user is partially hidden in that it isn't visible but the empty slot in the grid view is still there.                           |
| video_width             | 1280       | The virtual display and recording width in pixels.                                                                                                                                                                 |
| video_height            | 720        | The virtual display and recording height in pixels.                                                                                                                                                                |
| color_depth             | 24         | The color depth to use for the virtual framebuffer.                                                                                                                                                                |
| framerate               | 30         | The framerate that should be used for the recording.                                                                                                                                                               |
| audio_only              | false      | Specify whether audio only recording should be the default                                                                                                                                                         |
| audio_codec             | "wave"     | The audio codec to use for audio only recordings. The following options are supported: wave, flac, opus, aac and mp3. The audio codec used for video recordings is currently determined by the chosen video codec. |
| audio_bitrate           | "160k"     | The default audio bitrate to use. This will be used as a fallback if a codec specific audio bitrate hasn't been set. Please note that some codecs supports higher bitrates than others.                            |
| audio_aac_bitrate       | ""         | Bitrate to use for AAC                                                                                                                                                                                             |
| audio_mp3_bitrate       | ""         | Bitrate to use for mp3                                                                                                                                                                                             |
| audio_opus_bitrate      | ""         | Bitrate to use for opus                                                                                                                                                                                            |
| audio_thread_queue_size | 128        |                                                                                                                                                                                                                    |
| video_codec             | "x264"     | The video codec to use for the recording. Currently only x264 is supported.                                                                                                                                        |
| crf                     | 25         | The crf to use for the H.264 encoding.                                                                                                                                                                             |
| video_thread_queue_size | 32         |                                                                                                                                                                                                                    |
| encoding_preset         | "veryfast" | The encoding preset used for the H.264 encoding.                                                                                                                                                                   |
| encoding_threads        | 0          | How many threads to use for the encoding. 0 is auto.                                                                                                                                                               |

## Development setup
To setup a dev environment for coding, clone the repository and then run `make dev-setup` to setup a virtual environment with the needed dependencies.

For testing, a docker container is included in the repository as Talked only works on Linux. To build and run the container make sure you have docker installed for your OS. Then build the docker container using this command:
```
make dev-build
```

Then start the container using this command, it will take over the current terminal you have open. The command will start the docker container giving you a bash shell and a user with the same ID as your user on the host. The root of this project will also be passed through to the container in the /home/talked/talked folder. The container will get removed when you exit out of it, so you don't manually have to do it.
```
make dev-run
```

When you enter the container you will be placed in the /home/talked/talked folder, to get started first install the python dependencies using poetry.
```
poetry install --no-dev --no-root
```

Then create a config file called `config.toml` in the root of the project which contains the base URL for your Nextcloud instance. Below you can see the boilerplate:
```
base_url = "https://nextcloud.example.com"
```
The config file location is controlled by the `TALKED_CONFIG_PATH` env var and by default, in the container, it is set to the root of the project folder.

Now you can run the program either using:
```
poetry run python3 -m talked --host 0.0.0.0
```
Or by entering the virtualenv and then running the program. We bind the internal server to all interfaces so it can be easily access outside the docker container:
```
poetry shell

python3 -m talked --host 0.0.0.0
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

RuntimeDirectory=talked

Environment=TALKED_CONFIG_PATH=/opt/talked/config.toml

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

ExecStart=/opt/talked/talked/bin/uwsgi --http-socket /var/run/talked/talked.sock --die-on-term --master --manage-script-name --mount /=talked.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

This program is licensed under the AGPLv3 or later.
