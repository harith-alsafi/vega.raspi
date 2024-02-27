from typing import Optional, Callable, List
from flask import Flask, request, Response
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS cla
from threading import Thread
from vegapi.database import DataSeries
from vegapi.devices import Device
from vegapi.tools import Tool, tools_to_json
import signal

class RunFunction:
    name: str
    arguments: str

    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

class DataSeriesResult:
    title: str
    data: List[DataSeries]
    xLabel: str
    yLabel: str

    def __init__(self, title: str, data: list[DataSeries], xLabel: str, yLabel: str):
        self.title = title
        self.data = data
        self.xLabel = xLabel
        self.yLabel = yLabel

class FunctionResult:
    name: str
    result: str
    data: DataSeriesResult

    def __init__(self, name: str, result: str):
        self.name = name
        self.result = result

class VegaApi:
    app: Flask
    socketio: SocketIO
    onIndex: Callable[[], str]
    # takes list of function names
    onGetFunctions: Callable[[Optional[str]], List[Tool]]
    # takes list of RunFunction objects
    onRunFunctions: Callable[[list[RunFunction]], list[FunctionResult]]
    # takes list of component names 
    onGetComponents: Callable[[Optional[list[str]]], list[Device]] 

    # event emitter here for tool call run 
    def __init__(self, onGetFunctions: Callable[[Optional[str]], List[Tool]]):
        self.app = Flask(__name__)
        CORS(self.app) 
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.setup_routes()
        self.onGetFunctions = onGetFunctions

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return self.onIndex()

        @self.app.route('/get-functions', methods=['GET'])
        def get_functions():
            try:
                json_data = request.get_json()
                if json_data:
                    functions = self.onGetFunctions(json_data)
                    json_tools = tools_to_json(functions)
                    return Response(json_tools, content_type='application/json')
            except:
                functions = self.onGetFunctions(None)
                json_tools = tools_to_json(functions)
                return Response(json_tools, content_type='application/json')
            
            return None
        
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

    def run_flask_app(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, debug=False)

    def run(self):
        flask_thread = Thread(target=self.run_flask_app)
        flask_thread.setDaemon(True)
        
        def signal_handler(sig, frame):
            print("Ctrl+C pressed. Stopping Flask app...")
            print("Flask app stopped.")
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        flask_thread.start()