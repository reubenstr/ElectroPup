#!/usr/bin/python3
import os
import time
import zmq
import atexit
import argparse
import threading
from rich import print # Overrides print and injects colors
from flask import request, Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

###############################################################################
# Parameters
###############################################################################

FORWARD_DATA_RATE_LIMIT_MS = 0.050  # Throttle outgoing messages to clients

###############################################################################
# Flask App Setup
###############################################################################

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "dist")
app = Flask(__name__, static_folder=DIST_DIR, template_folder=DIST_DIR)

CORS(app)
app.config["SECRET_KEY"] = "secret_token_that_is_ok_to_be_hardcoded"

# Use threading-based async mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

###############################################################################
# Thread-local ZMQ sockets
###############################################################################

push_socket = None

def init_push_socket():
    global push_socket
    if push_socket is None:
        context = zmq.Context.instance()
        push_socket = context.socket(zmq.PUSH)
        push_socket.connect("tcp://127.0.0.1:5560")

def cleanup():
    global push_socket
    if push_socket:
        push_socket.close()
    zmq.Context.instance().term()

atexit.register(cleanup)          

###############################################################################
# Routes - Serve React Frontend
###############################################################################

@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

###############################################################################
# SocketIO Events
###############################################################################

@socketio.on("connect")
def handle_connect():
    ip = request.remote_addr
    print(f"Client connected from IP: {ip}")


@socketio.on("message")
def handle_message(msg):
    try:
        if push_socket is None:
            init_push_socket()
        push_socket.send_string(msg)
    except Exception as e:
        print(f"ZMQ send error: {e}")


@socketio.on("disconnect")
def handle_disconnect():
    ip = request.remote_addr
    print(f"Client disconnected from IP: {ip}")

###############################################################################
# Background Thread - Forward messages from ZMQ to SocketIO clients
###############################################################################

def forward_data_to_ui():
    print("Forwarding data thread starting")
    print(f"Message rate throttled to a message every {FORWARD_DATA_RATE_LIMIT_MS} seconds")

    context = zmq.Context.instance()
    pull_socket = context.socket(zmq.PULL)
    pull_socket.connect("tcp://127.0.0.1:5559")

    last_emit_time = 0

    while True:
        try:
            message = pull_socket.recv_string(flags=zmq.NOBLOCK)
            now = time.time()
            if now - last_emit_time >= FORWARD_DATA_RATE_LIMIT_MS:
                socketio.emit("message", message)
                last_emit_time = now
        except zmq.Again:
            time.sleep(0.01)  # No message, avoid busy waiting
        except zmq.ZMQError as e:
            print(f"ZMQ Error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

###############################################################################
# Main Entry Point
###############################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    is_dev = args.dev
    port = 5000 if is_dev else 80

    print(f"Running in {'development' if is_dev else 'production'} mode on port {port}")

    # Start background thread for forwarding ZMQ messages to UI
    threading.Thread(target=forward_data_to_ui, daemon=True).start()

    socketio.run(app, host="0.0.0.0", port=port, debug=is_dev)
