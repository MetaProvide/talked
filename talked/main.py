from flask import Flask
from talked import __version__
from talked import config
from talked import recorder
from threading import Thread

app = Flask(__name__)

config["recording"] = False
config["talk_room"] = ""


def main():
    app.run(host="0.0.0.0", threaded=False)


@app.route("/start", methods=["GET"])
def start():
    global config
    config["recording"] = True
    recording_thread = Thread(target=recorder.start)
    recording_thread.start()
    print("FOR THE LOVE OF GOD JUST RETURN")
    return "Setting up recorder..."


@app.route("/stop", methods=["GET"])
def stop():
    global config
    config["recording"] = False
    return "Stopping recorder..."


@app.route("/", methods=["GET"])
def info():
    return f"Version: {__version__} and recording is {config['recording']}"
