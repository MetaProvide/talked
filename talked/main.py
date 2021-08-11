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


@app.route("/start", methods=["POST"])
def start():
    global token
    if not recording.is_set():

        if request.get_json()["token"] == token:
            response = "A recording is already active in this room"
        else:
            response = "A recording is currently active in another room"

        return jsonify(message=response)

    base_url = request.get_json()["base_url"]
    token = request.get_json()["token"]

    recording.clear()
    recording_thread = Thread(
        target=recorder.start, args=(base_url, token, queue, recording)
    )
    recording_thread.start()
    output = queue.get()

    if output["status"] == "error":
        recording.set()
        token = ""

    return jsonify(message=output["message"])


@app.route("/stop", methods=["POST"])
def stop():
    global token

    if request.get_json()["token"] == token:
        recording.set()
        token = ""
        output = queue.get()
        return jsonify(message=output["message"])

    return jsonify(
        message="A recording is currently active in another room and can only be stopped from that room."
    )


@app.route("/status", methods=["POST"])
def status():
    if not recording.is_set():

        if request.get_json()["token"] == token:
            response = "A recording is currently active in this room"
        else:
            response = "A recording is currently active in another room"

        return jsonify(message=response)

    return jsonify(message="No recording is currently active")


@app.route("/", methods=["GET"])
def info():
    return jsonify(version=__version__)
