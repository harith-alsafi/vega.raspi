# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS cla

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app) 

@app.route('/connect')
def connect():
    return "hi"

@app.route('/')
def home():
    return 'Hello, this is a Flask-SocketIO example without using index.html!'

@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    socketio.emit('message', message)  # Broadcast the message to all connected clients

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
