import os
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

ids = []
clients = []
rooms_online = []

@app.route("/")
def index():
    return render_template("index.html", ids = ids)

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

@socketio.on("create-room")
def add_room(data):
    name = data["name"]
    room_name = data["room"]

    t = time.localtime()
    time_now = f"{t.tm_hour}:{t.tm_min}"
    rooms_online.append(room_name)

    join_room(room_name)

    emit("new_member", {"name":name, "time": time_now}, broadcast=True, room=room_name)


@socketio.on("jroom")
def j_room(data):
    name = data["name"]
    room_name = data["room"]

    t = time.localtime()
    time_now = f"{t.tm_hour}:{t.tm_min}"

    if not room_name in rooms_online:
        emit("new_member", {"success":True}, broadcast=True, room=request.sid)

    else:
        join_room(room_name)
        emit("new_member", {"name":name, "time": time_now}, broadcast=True, room=room_name)


@socketio.on("message-room")
def roomspam(data):
    print("ontvangen")
    text = data["selection"]
    name = data["name"]
    room_name = data["room"]
    t = time.localtime()
    time_now = f"{t.tm_hour}:{t.tm_min}"

    print("send")
    if not room_name:
        emit("new_member", {"success":False})
    else:
        emit("message-room", {"text": text, "name":name, "time":time_now},
             broadcast=True, room = room_name)

@socketio.on("submit-name")
def vote(data):
    id = request.sid
    for i in ids:
        if data["name"] == i["name"]:
            break
    else:
        print("{} connected".format(id))
        clients.append(id)
        ids.append({"name":data["name"], "sid":id})
        emit("contacts", {"name":data["name"], "sid":id}, broadcast=True)


@app.route("/name_change", methods=["GET", "POST"])
def name_change():
    return render_template("name_change.html")


@app.route("/name_check", methods=["POST"])
def check_name():
    new_name = request.form.get("new_name")
    old_name = request.form.get("old_name")

    if not new_name or not old_name:

        return jsonify({"success":False})

    for i in ids:
        if new_name == i["name"]:
            return jsonify({"success":False})

    for i in ids:
        if old_name == i["name"]:
            sid = i["sid"]
            ids.pop(ids.index(i))
            ids.append({"name":new_name, "sid":sid})
            break
    else:
        return jsonify({"success":False})

    return jsonify({"success":True, "name":new_name})

@app.route("/rooms", methods=["POST", "GET"])
def rooms():
    return render_template("rooms.html")
