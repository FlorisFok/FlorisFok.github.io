import os
import requests
import time

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room
from flask_socketio import SocketIO, emit
from flask import Flask, flash, jsonify, redirect, render_template, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("layout.html")

@socketio.on("message")
def spam(data):
    text = data["selection"]
    name = data["name"]
    sid = data["sid"]
    t = time.localtime()
    time_now = f"{t.tm_hour}:{t.tm_min}"

    if sid == "None":
        emit("message", {"text": text, "name":name, "time":time_now}, broadcast=True)
    else:
        for id in [sid, request.sid]:
            emit("message", {"text": text, "name":name, "time":time_now}, broadcast=True, room=id)
