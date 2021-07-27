# Talked

Call recording for Nextcloud Talk

## Dependencies

### Apt

* python3
* python3-pip
* firefox-geckodriver
* pulseaudio
* xvfb
* ffmpeg

### Python

* selenium
* PyVirtualDisplay

## Pulse

pacmd load-module module-null-sink sink_name=MySink


## Todo

* Handle filename conflicts
* Hide sidebar and go full screen before starting the recording.
* Disable microphone
* Rename user when joining
* Support using a authenticated user
* Support using chromium based browser
* Implement Talk chat commands
* Option to enable and disable recording of chat
