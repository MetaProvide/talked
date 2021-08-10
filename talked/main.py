from flask import Flask
from flask import jsonify
from flask import request
from talked import recorder
from threading import Thread
from threading import Event
from queue import Queue
from talked import __version__

app = Flask(__name__)

token = ""
queue = Queue()
recording = Event()
recording.set()


def main():
    app.run(host="0.0.0.0", threaded=False)


@app.route("/start", methods=["GET"])
def start():
    recording.clear()
    recording_thread = Thread(target=recorder.start, args=(queue, recording))
    recording_thread.start()
    output = queue.get()
    return jsonify(message=output)


@app.route("/stop", methods=["GET"])
def stop():
    recording.set()
    output = queue.get()
    return jsonify(message=output)


@app.route("/status", methods=["POST"])
def status():
    if not recording.is_set():

        if request.get_json()["token"] == token:
            output = "A recording is currently active in this room"
        else:
            output = "A recording is currently active in another room"

        return jsonify(message=output)

    return jsonify(message="No recording is currently active")


@app.route("/", methods=["GET"])
def info():
    return jsonify(version=__version__)
