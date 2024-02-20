from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS cla
from threading import Thread

class VegaApi:
    app: Flask
    socketio: SocketIO
    # event emitter here for tool call run 
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app) 
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return 'Hello, World!'

        @self.app.route('/connect')
        def control_circuit():
            return 'Connected to the circuit!'
        
        @self.socketio.on('message')
        def handle_message(message):
            print('Received message:', message)
            self.socketio.emit('message', message)  # Broadcast the message to all connected clients

    def _run_flask_app(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=True)

    def run(self):
        flask_thread = Thread(target=self._run_flask_app)
        flask_thread.start()