
import os
import requests
import time
import socket_control as SC
from moreFunctions import time_str, list2jsonlist

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room
from flask_socketio import SocketIO, emit
from flask import Flask, flash, jsonify, redirect, render_template, request, session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Activate the cocketclass
main_socket = SC.socketServer()

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("message")
def message(data):
    # Extract data
    text = data["selection"]
    name = data["sender"]
    to_name = data["reciever"]

    # Compose json message with time stamp
    message = {"text": text, "name":name, "time":time_str()}

    # Send message and save to history, for both, or for all
    if not to_name == "None":
        main_socket.add_message_user(name, message)
        main_socket.add_message_user(to_name, message)
        main_socket.send_message(message, user=name)
        main_socket.send_message(message, user=to_name)
    else:
        # If to_name == None, the message is for everybody
        for name in main_socket.get_names():
            main_socket.add_message_user(name, message)
        main_socket.send_message(message, user=to_name)


@socketio.on("create-room")
def add_room(data):
    # Extract data
    name = data["name"]
    room_name = data["room"]

    # Check if room is free
    if main_socket.room_name_taken(room_name):
        return main_socket.send_message({"success":False},
                                        room_name=request.sid,
                                        emit_str="new_member")

    # Add_room
    main_socket.add_room(room_name)
    main_socket.user2room(name, room_name)

    # Send message that somebody joined
    json_package = {"name":name, "time": time_str()}
    main_socket.send_message(json_package,
                             room_name=room_name,
                             emit_str="new_member")

    # Get active rooms and send data in json
    list_package = main_socket.get_rooms()

    jsonlist_package = list2jsonlist(list_package, "name")
    main_socket.send_message(jsonlist_package,
                             user="None",
                             emit_str="rooms")

    # Get history and send data
    json_package = main_socket.get_messages(room = room_name)
    if json_package:
        main_socket.send_message(json_package[:100],
                                 sid=request.sid,
                                 emit_str="history-response")


@socketio.on("jroom")
def j_room(data):
    # Extract data
    name = data["name"]

    # Check if request for reload or joining room
    try:
        room_name = data["room"]
    except:
        room_name = False

    if room_name:
        # Checks if room is live
        if not main_socket.room_name_taken(room_name):
            json_package = {"success":False}
            main_socket.send_message(json_package,
                                     sid=request.sid,
                                     emit_str="new_member")
        # Adds user to room
        else:
            main_socket.user2room(name, room_name)
            json_package = {"name":name, "time": time_str()}
            main_socket.send_message(json_package,
                                     room_name=room_name,
                                     emit_str="new_member")

    # Returns all rooms live
    list_package = main_socket.get_rooms()
    jsonlist_package = list2jsonlist(list_package, "name")
    main_socket.send_message(jsonlist_package,
                             user="None",
                             emit_str="rooms")

    # Returns all messages in room
    json_package = main_socket.get_messages(room = room_name)
    if json_package:
        main_socket.send_message(json_package[:100],
                                 sid=request.sid,
                                 emit_str="history-response")


@socketio.on("message-room")
def roomspam(data):
    # Extract data
    text = data["selection"]
    name = data["name"]
    room_name = data["room"]

    # Checks if room is live
    if not room_name or not main_socket.room_name_taken(room_name):
        main_socket.send_message({"success":False},
                                 sid=request.sid,
                                 emit_str="new_member")
    # Sends message to correct room
    else:
        message = {"text": text, "name":name, "time":time_str()}
        main_socket.add_message_room(room_name, message)
        main_socket.send_message(message,
                                 room_name=room_name,
                                 emit_str="message-room")

@socketio.on("history-call")
def history_retrive(data):
    # First checks if we have a room or private chat.
    try:
        # Send history with a max of 100pieces to user
        name = data['name']
        json_package = main_socket.get_messages(name = name)
        if json_package:
            main_socket.send_message(json_package[:100],
                                         sid=request.sid,
                                         emit_str="history-response")
    except:
        pass
    try:
        # Send history with a max of 100pieces to room user
        room_name = data["room"]
        json_package = main_socket.get_messages(room = room_name)
        if json_package:
            main_socket.send_message(json_package[:100],
                                     sid=request.sid,
                                     emit_str="history-response")
    except:
        pass

@socketio.on("submit-name")
def vote(data):
    # Extract data
    id = request.sid
    name = data["name"]

    # Checks if name is in use, other wise resets SessionID
    if not main_socket.username_taken(name):
        main_socket.add_user(name, id)
    else:
        # Reset session ID, without losing info
        json_message = main_socket.get_messages(name = name)
        main_socket.remove_user(name)
        main_socket.add_user(name, request.sid)
        for message in json_message:
            main_socket.add_message_user(name, message)

    # Confirms connection
    print("{} connected as {}".format(id,name))

    # Send contact list
    json_package = main_socket.get_users()
    main_socket.send_message(json_package,
                             room_name="MAIN",
                             emit_str="contacts")


@app.route("/rooms", methods=["POST", "GET"])
def rooms():
    return render_template("rooms.html")


@app.route("/name_change", methods=["GET", "POST"])
def name_change():
    return render_template("name_change.html")

# AJAX REQUEST
@app.route("/name_check", methods=["POST"])
def check_name():
    # Extract data
    new_name = request.form.get("new_name")
    old_name = request.form.get("old_name")

    # Some checks
    if not new_name or not old_name:
        return jsonify({"success":False})
    if main_socket.username_taken(new_name):
        return jsonify({"success":False})
    if main_socket.username_taken(old_name):
        # Change of username
        main_socket.change_username(old_name, new_name)
    else:
        return jsonify({"success":False})
    # If success, return True and new name for sessionStorage
    return jsonify({"success":True, "name":new_name})
