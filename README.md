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

* Add custom CSS to hide unwanted elements
* Make delay a bit longer to make sure the full screen popup isn't capture on video
* Rename user when joining
* Handle filename conflicts
* Support using a authenticated user
* Support using chromium based browser
* Implement Talk chat commands
* Option to enable and disable recording of chat
