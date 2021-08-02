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

## Dev setup

### VSCode

If you are using VSCode as your editor make sure you have the Remote - Containers plugin installed. You can find a link to the plugin [here](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) with instructions on how to install the required dependencies and how to use the plugin.

When the connection to the container has been setup run `poetry install` to install the required python dependencies and then you can run the program with `python3 talked/__init__.py`

### Generic

Make sure you have docker installed for your OS. Then build the generic docker container using this command
```
docker build . -f .devcontainer/Dockerfile.generic -t talked
```

Then start the container using this command, it will take over the current terminal you have open. The command will start the docker container giving you a bash shell and a user with the same ID as your user on the host. The root of this project will also be passthrough to the container in the /talked folder. The container will get removed when you exit out of it so you don't manually have to do it.
```
docker run --rm -it --user "$(id -u):$(id -g)" -v "$(pwd):/talked" talked bash
```

When you enter the container you will be placed in the /talked folder, to get started first install the python dependencies using poetry.
```
poetry install --no-root
```

Then you can run the program as below:
```
python3 talked/__init__.py
```

### Both

The last thing is to create a public call on your Nextcloud instance of choice and paste the call link between the quotes on line 79 where it says `driver.get("")`. Then join the call yourself and run the program.

## Todo

- [x] Rename user when joining
- [x] Handle filenames
- [x] Add custom CSS to hide unwanted elements
- [x] Figure out default transcoding settings
- [ ] Create config file
- [ ] Integrate into Talk
- [ ] Create setup for running on Nextcloud server or remote server
- [ ] Create docker container

## Later
* Option to enable and disable recording of chat
* Support using chromium based browser
* Support using a authenticated user
* Add options to control transcoding
* When using authenticated user, add option to auto add the recording user when recording non public chat.

## License

This program is licensed under the AGPLv3 or later.
