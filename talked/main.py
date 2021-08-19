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

    token = request.get_json()["token"]

    recording.clear()
    recording_thread = Thread(target=recorder.start, args=(token, queue, recording))
    recording_thread.start()
    output = queue.get()

    if output["status"] == "error":
        recording.set()
        token = ""

    return jsonify(message=output["message"])


@app.route("/stop", methods=["POST"])
def stop():
    global token

    if not recording.is_set():
        if request.get_json()["token"] == token:
            recording.set()
            token = ""
            output = queue.get()
            response = output["message"]
        else:
            response = (
                "A recording is currently active in another room and "
                "can only be stopped from that room."
            )

        return jsonify(message=response)

    return jsonify(message="No recording is currently active")


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
    return jsonify(message=f"version: {__version__}")
