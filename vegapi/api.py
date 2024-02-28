import json
from typing import Optional, Callable, List
from flask import Flask, Request, request, Response
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS cla
from threading import Thread
from vegapi.database import DataSeries
from vegapi.devices import Device, devices_to_json
from vegapi.tools import Tool, tools_to_json
import signal

class RunTool:
    name: str
    arguments: str

    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments
    
    def to_json(self):
        return {
            "name": self.name,
            "arguments": self.arguments
        }

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

    def to_json(self):
        return {
            "title": self.title,
            "data": [data.to_json() for data in self.data],
            "xLabel": self.xLabel,
            "yLabel": self.yLabel
        }

class ToolResult:
    name: str
    result: str
    status: bool
    data: Optional[DataSeriesResult]

    def __init__(self, name: str, result: str, status: bool, data: Optional[DataSeriesResult] = None):
        self.name = name
        self.result = result
        self.status = status
        self.data = data

    def to_json(self):
        return {
            "name": self.name,
            "result": self.result,
            "status": self.status,
            **({'data': self.data} if self.data else {})
        }
    
def run_tools_to_json(tools: List[ToolResult]):
    return json.dumps([tool.to_json() for tool in tools], indent=4)

class VegaApi:
    app: Flask
    socketio: SocketIO
    # takes list of function names
    onGetTools: Callable[[Optional[List[str]]], List[Tool]]
    # takes list of RunFunction objects
    onRunTools: Callable[[list[RunTool]], list[ToolResult]]
    # takes list of component names 
    onGetDevices: Callable[[Optional[list[str]]], list[Device]] 

    # event emitter here for tool call run 
    def __init__(self, onGetTools: Callable[[Optional[str]], List[Tool]], onRunTools: Callable[[list[RunTool]], list[ToolResult]], onGetDevices: Callable[[Optional[list[str]]], list[Device]]):
        self.app = Flask(__name__)
        CORS(self.app) 
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.setup_routes()
        self.onGetTools = onGetTools
        self.onRunTools = onRunTools
        self.onGetDevices = onGetDevices

    def get_tools(self, req: Request) -> Response:
        try:
            json_data = req.get_json(force=True, silent=True)
            if json_data:
                get_tools: List[str] = json_data
                tools = self.onGetTools(get_tools)
                json_tools = tools_to_json(tools)
            else:
                raise Exception("No data provided")
            return Response(json_tools, content_type='application/json')
        except:
            tools = self.onGetTools(None)
            json_tools = tools_to_json(tools)
            return Response(json_tools, content_type='application/json')
 
    
    def run_tools(self, req: Request) -> Response:
        try:
            json_data = req.get_json(force=True, silent=True)
            if json_data:

                run_tools = [RunTool(tool['name'], tool['arguments']) for tool in json_data]
                results = self.onRunTools(run_tools)
                json_results = run_tools_to_json(results)
                return Response(json_results, content_type='application/json')
            else:
                raise Exception("No data provided")
        except:
            return Response("No data provided", content_type='application/json')

    def get_devices(self, req: Request) -> Response:
        try:
            json_data = req.get_json(force=True, silent=True)
            if json_data:
                get_devices: List[str] = json_data
                devices = self.onGetDevices(get_devices)
                json_devices = devices_to_json(devices=devices)
            else:
                raise Exception("No data provided")
            return Response(json_devices, content_type='application/json')
        except:
            devices = self.onGetDevices(None)
            json_devices = devices_to_json(devices=devices)
            return Response(json_devices, content_type='application/json')

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return "Raspberry Pi Flask Server"

        @self.app.route('/get-tools', methods=['GET', 'POST'])
        def get_tools():
            return self.get_tools(request)
        
        @self.app.route('/run-tools', methods=['GET', 'POST'])
        def run_tools():
            return self.run_tools(request)

        @self.app.route('/get-devices', methods=['GET', 'POST'])
        def get_devices():
            return self.get_devices(request)

    def run_flask_app(self):
        # 5000 doesnt work on windows but works on raspi 
        self.socketio.run(self.app, host='0.0.0.0', port=7000, debug=False) 

    def run(self):
        flask_thread = Thread(target=self.run_flask_app)
        flask_thread.setDaemon(True)

        def signal_handler(sig, frame):
            print("Ctrl+C pressed. Stopping Flask app...")
            print("Flask app stopped.")
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        flask_thread.start()