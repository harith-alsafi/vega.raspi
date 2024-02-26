from typing import Optional
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS cla
from threading import Thread

from dataclasses import dataclass

class RunFunction:
    name: str
    arguments: str

    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

class VegaApi:
    app: Flask
    socketio: SocketIO
    onIndex: callable[[], str]
    # takes list of function names
    onGetFunctions: callable[[Optional[str]], str]
    # takes list of RunFunction objects
    onRunFunctions: callable[[list[RunFunction]], str]#
    # takes list of component names 
    onGetComponents: callable[[Optional[list[str]]], str] 

    # event emitter here for tool call run 
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app) 
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return self.onIndex()

        @self.app.route('/get-functions')
        def get_functions():
            return self.onGetFunctions()
        
        @self.app.route('/run-functions')
        def run_functions():
            return self.onRunFunctions()

        @self.app.route('/get-components')
        def get_components():
            return self.onGetComponents()

        @self.socketio.on('message')
        def handle_message(message):
            print('Received message:', message)
            self.socketio.emit('message', message)  # Broadcast the message to all connected clients

    def _run_flask_app(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True)

    def run(self):
        flask_thread = Thread(target=self._run_flask_app)
        flask_thread.start()