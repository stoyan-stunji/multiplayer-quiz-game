import socket
import subprocess
import sys
import time
import threading
import requests
from engineio import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# ----------------------------
# Question Management
# ----------------------------

def load_questions(filename="questions.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            questions = json.load(f)
            print(f"Loaded {len(questions)} questions from {filename}")
            return questions
    except FileNotFoundError:
        print(f"Error - file {filename} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing {filename}: {e}")
        sys.exit(1)

# ----------------------------
# Player Management
# ----------------------------

class PlayerManager:
    def __init__(self):
        self.players = {}

    def register(self, name, sid):
        if name not in self.players:
            self.players[name] = {"score": 0, "sid": sid, "current_question": 0}
        else:
            self.players[name]["sid"] = sid
        return self.players[name]

    def get_by_sid(self, sid):
        for name, pdata in self.players.items():
            if pdata.get("sid") == sid:
                return name, pdata
        return None, None

    def disconnect(self, sid):
        for name, pdata in self.players.items():
            if pdata.get("sid") == sid:
                self.players[name]["sid"] = None
                return

# ----------------------------
# Leaderboard
# ----------------------------

def get_leaderboard(players):
    leaderboard = [{"name": n, "score": p["score"]} for n, p in players.items()]
    return sorted(leaderboard, key=lambda x: x["score"], reverse=True)

# ----------------------------
# Networking / Utils
# ----------------------------

def find_free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def start_ngrok(port):
    try:
        proc = subprocess.Popen(["ngrok", "http", str(port)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(15):
            try:
                tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
                public_url = tunnels["tunnels"][0]["public_url"]
                print("\n🎉 Game is live! Open this on your phone:")
                print(f"{public_url}/join?name=YourName")
                print(f"Leaderboard: {public_url}/leaderboard\n")
                return proc
            except:
                time.sleep(1)
    except Exception as e:
        print("Error starting ngrok:", e)
    return None

# ----------------------------
# Flask / SocketIO App
# ----------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

questions = load_questions()
players = PlayerManager()

@app.route("/")
def index():
    return "Go to /join?name=YourName to join the game. Visit /leaderboard to see scores."

@app.route("/join")
def join():
    name = request.args.get("name", f"Player{len(players.players) + 1}")
    return render_template("player.html", name=name)

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html")

# ----------------------------
# Socket Events
# ----------------------------

@socketio.on("connect")
def on_connect():
    print(f"New connection: {request.sid}")

@socketio.on("disconnect")
def on_disconnect():
    players.disconnect(request.sid)
    socketio.emit("leaderboard_update", get_leaderboard(players.players))

@socketio.on("register")
def on_register(data):
    pdata = players.register(data["name"], request.sid)
    emit("message", {"msg": f"Welcome, {data['name']}! Score: {pdata['score']}"})
    emit("score", {"score": pdata["score"]})
    send_question(request.sid, pdata["current_question"])
    socketio.emit("leaderboard_update", get_leaderboard(players.players))

@socketio.on("answer")
def on_answer(data):
    name, pdata = players.get_by_sid(request.sid)
    if not name:
        return
    q = questions[pdata["current_question"] % len(questions)]
    points = q["points"].get(data["choice"], 0)
    pdata["score"] += points
    pdata["current_question"] = (pdata["current_question"] + 1) % len(questions)
    emit("message", {"msg": f"You got {points} points!"})
    emit("score", {"score": pdata["score"]})
    send_question(request.sid, pdata["current_question"])
    socketio.emit("leaderboard_update", get_leaderboard(players.players))

# ----------------------------
# Question Sending
# ----------------------------

def send_question(sid, question_index):
    q = questions[question_index % len(questions)]
    socketio.emit("question", q, room=sid)

# ----------------------------
# Stop Command Listener
# ----------------------------

import os

def listen_for_stop(proc):
    while True:
        cmd = input()
        if cmd.strip().lower() == "stop":
            print("Stopping the game...")

            # Kill ngrok if running
            if proc:
                proc.terminate()

            # Hard kill the Python process (all threads, server, etc.)
            os._exit(0)


# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    port = find_free_port()
    print(f"Starting server on port {port}...")
    ngrok_proc = start_ngrok(port)
    threading.Thread(target=listen_for_stop, args=(ngrok_proc,), daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=port)
