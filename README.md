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

Make sure you have docker installed for your OS. Then build the generic docker container using this command
```
docker build docker -f docker/Dockerfile.dev -t talked
```

Then start the container using this command, it will take over the current terminal you have open. The command will start the docker container giving you a bash shell and a user with the same ID as your user on the host. The root of this project will also be passthrough to the container in the /home/talked/talked folder. The container will get removed when you exit out of it so you don't manually have to do it.
```
docker run --rm -it -v "$(pwd):/home/talked/talked" -e "UID=$(id -u)" -e "GID=$(id -g)" -p "5000:5000" talked
```

When you enter the container you will be placed in the /home/talked/talked folder, to get started first install the python dependencies using poetry.
```
poetry install
```

Then you can run the program either using:
```
poetry run python3 -m talked
```
Or by entering the virtualenv and then running the program:
```
poetry shell

python3 -m talked
```

### Both

The last thing to do is create a file called `config.json` in the root of the project which contains a link to a public Nextcloud Talk room. Below you can see the boilerplate:
```
{
  "base_url": "",
  "log_level": 20
}
```

Lastly remember to join the call before starting the program, as it will only join if there is a call in progress.

## License

This program is licensed under the AGPLv3 or later.
