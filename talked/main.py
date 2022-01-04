from queue import Queue
from threading import Event, Thread

from flask import Flask, jsonify, request

from talked import __version__, config, recorder

app = Flask(__name__)

token = ""  # nosec
queue: Queue = Queue()
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
    nextcloud_version = request.get_json().get(["nextcloud_version"], "22")

    audio_only = request.get_json().get("audio_only", config["audio_only"])
    grid_view = request.get_json().get("grid_view", config["grid_view"])

    recording.clear()
    recording_thread = Thread(
        target=recorder.start,
        args=(token, queue, recording, nextcloud_version, audio_only, grid_view),
    )
    recording_thread.start()
    output = queue.get()

    if output["status"] == "error":
        recording.set()
        token = ""  # nosec

    return jsonify(message=output["message"])


@app.route("/stop", methods=["POST"])
def stop():
    global token

    if not recording.is_set():
        if request.get_json()["token"] == token:
            recording.set()
            token = ""  # nosec
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
