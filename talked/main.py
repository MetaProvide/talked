from flask import Flask
from talked import __version__
from talked import config
from talked import recorder

app = Flask(__name__)

config["recording"] = False
config["talk_room"] = ""


def main():
    app.run(host="0.0.0.0")


@app.route("/start", methods=["GET"])
def start():
    global config
    config["recording"] = True
    recorder.init()
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
