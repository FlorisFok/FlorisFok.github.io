import os
import requests
import time

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room
from flask_socketio import SocketIO, emit
from flask import Flask, flash, jsonify, redirect, render_template, request, session


class socketServer(object):
    '''
    Some custom room handeling, since the documentation is scares, and keeps
    kicking things out of rooms. (MAIN is still hard coded...)
    '''
    def __init__(self):
        self.users = [] # expandable
        self.rooms = {"MAIN":{"sids":[],"users":[], "messages":[]}}
        self.sid = [] # fast check
        self.names = [] # fast check

    def __str__(self):
        pass

    def get_names(self):
        return self.names

    def get_users(self):
        return self.users

    def get_rooms(self):
        return list(self.rooms)

    def add_message_room(self, room_name, message):
        '''
        Adds a message in form of a dict to the message list of a room
        '''
        self.rooms[room_name]["messages"].append(message)

    def add_message_user(self, user, message):
        '''
        Adds a message in form of a dict to the message list of an user
        '''
        # Find right spot in dict and list to append to.
        for i,li in enumerate(self.users):
            if li["name"] == user:
                self.users[i]["messages"].append(message)

    def add_user(self, name, sid):
        '''
        Add new user to all the documentation
        '''
        self.users.append({"name":name,"sid":sid, "messages":[]})
        self.sid.append(sid)
        self.names.append(name)

        # Always add every body to MAIN
        self.user2room(name, 'MAIN')
        return True

    def username_taken(self, name):
        '''
        Checks if username is username_taken
        returns boolean
        '''
        if name in self.names:
            return True
        else:
            return False

    def change_username(self, old_name, new_name):
        '''
        Changes the username of an user
        '''
        # Get old info.
        old_sid = self.get_sid(old_name)
        # Change user in the rooms
        for room in self.rooms.keys():
            # Save all data
            names = self.rooms[room]["users"]
            ids = self.rooms[room]["sids"]
            mes = self.rooms[room]["messages"]
            for name in names:
                if name == old_name:
                    names.pop(names.index(old_name))
                    names.append(new_name)
            # Overwrite data, with or without changes
            self.rooms.pop(room)
            self.rooms[room] = {"sids":ids,"users":names,"messages":mes}

        # Remove from list and users
        self.remove_user(old_name)
        self.add_user(new_name, old_sid)
        return True

    def remove_user(self, name):
        '''
        Removes user from contacts and rooms
        '''
        for li in self.users:
            # Find user dict
            if li["name"] == name:
                sid_u = li["sid"]
                # Remove out rooms
                for room_name in self.rooms:
                    try:
                        self.user_out_room(name, room_name)
                    except:
                        pass
                self.users.pop(self.users.index(li))
                self.sid.pop(self.sid.index(sid_u))
                self.names.pop(self.names.index(name))
                return True
        else:
            # if failed
            return False

    def get_sid(self, user):
        '''
        Get session id from user
        '''
        for li in self.users:
            if li["name"] == user:
                return li["sid"]
        else:
            return False

    def add_room(self, room_name):
        '''
        Add a room
        '''
        self.rooms[room_name] = {"sids":[], "users":[], "messages":[]}
        return True

    def room_name_taken(self, room_name):
        '''
        Checks if room is taken
        return boolean
        '''
        if room_name in self.rooms:
            return True
        else:
            return False

    def remove_room(self, room_name):
        '''
        Removes a room from the room dict
        '''
        return self.rooms.pop(room_name)

    def user2room(self, user, room_name):
        '''
        Adds user to a room
        '''
        try:
            self.rooms[room_name]["sids"].append(self.get_sid(user))
            self.rooms[room_name]["users"].append(user)
            return True
        except:
            return False

    def user_out_room(self, user, room_name):
        '''
        Removes user from room
        returns removed name
        '''
        sid = self.get_sid(user)

        # Checks index, in order to pop the item
        i = self.rooms[room_name]["sids"].index(sid)
        self.rooms[room_name]["sids"].pop(i)
        i = self.rooms[room_name]["users"].index(user)
        return self.rooms[room_name]["users"].pop(i)

    def send_message(self, json_message, room_name = False,
                     user = False, sid = False, emit_str = "message"):
        '''
        Send message by choosen channel, user, room or sid. user=None => all
        '''
        if room_name:
            # Send to room
            for sid in self.rooms[room_name]["sids"]:
                emit(emit_str,
                     json_message,
                     broadcast=True, room=sid)

        elif user == "None":
            # Send to all
            emit(emit_str,
                 json_message,
                 broadcast = True)

        elif user:
            # Send to user
            user_sid = self.get_sid(user)
            emit(emit_str,
                 json_message,
                 broadcast=True, room=user_sid)

        elif sid:
            # Send to sid
            emit(emit_str,
                 json_message,
                 broadcast=True, room=sid)

        else:
            # Error
            raise("Please enter username or room name!")
            return False

    def get_messages(self, name = '', room = ''):
        if len(name) > 0:
            for i,li in enumerate(self.users):
                if li["name"] == name:
                    return self.users[i]["messages"]

        elif len(room) > 0:
            return self.rooms[room]["messages"]

        else:
            print("Please enter username or room")
