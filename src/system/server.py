import os
import time
import zmq
import atexit
import argparse
import threading
from rich import print  # Overrides print and injects colors
from flask import request, Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

###############################################################################
# Parameters
###############################################################################

FORWARD_DATA_RATE_LIMIT_SEC = 0.050 
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "dist")

###############################################################################
# Flask App Setup
###############################################################################

app = Flask(__name__, static_folder=DIST_DIR, template_folder=DIST_DIR)
CORS(app)
app.config["SECRET_KEY"] = "secret_token_that_is_ok_to_be_hardcoded"

# Threading mode keeps compatibility without monkey-patching
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

###############################################################################
# ZMQ Setup (initialized once at startup)
###############################################################################

context = zmq.Context.instance()
push_socket = context.socket(zmq.PUSH)
push_socket.connect("tcp://127.0.0.1:5560")

pull_socket = context.socket(zmq.PULL)
pull_socket.connect("tcp://127.0.0.1:5559")

###############################################################################
# Graceful Shutdown Control
###############################################################################

stop_event = threading.Event()

def cleanup():
    print("[yellow]Cleaning up ZMQ sockets and context...[/yellow]")
    try:
        push_socket.close(0)
        pull_socket.close(0)
    except Exception as e:
        print(f"[red]Error closing sockets: {e}[/red]")
    context.term()
    stop_event.set()

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
    print(f"[green]Client connected from IP: {ip}[/green]")

@socketio.on("message")
def handle_message(msg):
    try:
        push_socket.send_string(msg)
    except Exception as e:
        print(f"[red]ZMQ send error: {e}[/red]")

@socketio.on("disconnect")
def handle_disconnect():
    ip = request.remote_addr
    print(f"[yellow]Client disconnected from IP: {ip}[/yellow]")

###############################################################################
# Background Thread - Forward messages from ZMQ to SocketIO clients
###############################################################################

def forward_data_to_ui():
    print("[cyan]Forwarding data thread starting[/cyan]")
    print(f"[cyan]Message rate throttled to {FORWARD_DATA_RATE_LIMIT_SEC * 1000:.0f}ms[/cyan]")

    last_emit_time = 0

    while not stop_event.is_set():
        try:
            message = pull_socket.recv_string(flags=zmq.NOBLOCK)
            now = time.time()
            if now - last_emit_time >= FORWARD_DATA_RATE_LIMIT_SEC:
                # Use start_background_task to ensure thread-safety with any async mode
                socketio.start_background_task(socketio.emit, "message", message)
                last_emit_time = now
        except zmq.Again:
            time.sleep(0.005)  # Avoid busy waiting
        except zmq.ZMQError as e:
            if not stop_event.is_set():
                print(f"[red]ZMQ Error: {e}[/red]")
            break
        except Exception as e:
            print(f"[red]Unexpected error: {e}[/red]")
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

    print(f"[bold]Running in {'development' if is_dev else 'production'} mode on port {port}[/bold]")

    # Start background thread for forwarding ZMQ messages to UI
    forward_thread = threading.Thread(target=forward_data_to_ui, daemon=True)
    forward_thread.start()

    try:
        socketio.run(app, host="0.0.0.0", port=port, debug=is_dev, allow_unsafe_werkzeug=True )
    except KeyboardInterrupt:
        print("[yellow]Shutting down due to keyboard interrupt...[/yellow]")
        cleanup()
