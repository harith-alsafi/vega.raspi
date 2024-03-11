import json
from typing import Literal, Optional, Callable, List, Union
from flask import Flask, Request, request, Response
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS cla
from threading import Thread
from vegapi.database import DataPlot, DataSeries, DataSeriesModel
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

UiType = Literal["flow-chart" , "plot" , "cards" , "image", "table", "map"]

class ToolResult:
    name: str
    result: str
    error: Optional[str]
    data: Optional[Union[DataPlot, str, Device]]
    ui: Optional[UiType]

    def __init__(self, name: str, result: str, error: Optional[str] = None, data: Optional[Union[DataPlot, str, Device]] = None, ui: Optional[UiType] = None):
        self.name = name
        self.result = result
        self.error = error
        self.data = data
        self.ui = ui

    def to_json(self):
        data = self.data.to_json() if isinstance(self.data, DataPlot) else self.data.to_json() if isinstance(self.data, Device) else self.data
        return {
            "name": self.name,
            "result": self.result,
            "error": self.error,
            "ui": self.ui,
            "data": self.data
        }
    
def run_tools_to_json(tools: List[ToolResult]):
    return json.dumps([tool.to_json() for tool in tools], indent=4)

GetToolsReturnType = Union[List[Tool], Response]
RunToolsReturnType = Union[List[ToolResult], Response]
GetDevicesReturnType = Union[List[Device], Response]

class VegaApi:
    app: Flask
    socketio: SocketIO
    # takes list of function names
    onGetTools: Callable[[Optional[List[str]]], GetToolsReturnType]
    # takes list of RunFunction objects
    onRunTools: Callable[[list[RunTool]], RunToolsReturnType]
    # takes list of component names 
    onGetDevices: Callable[[Optional[list[str]]], GetDevicesReturnType] 

    # event emitter here for tool call run 
    def __init__(self, onGetTools: Callable[[Optional[str]], GetToolsReturnType], onRunTools: Callable[[list[RunTool]], RunToolsReturnType], onGetDevices: Callable[[Optional[list[str]]], GetDevicesReturnType]):
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
                if isinstance(tools, Response):
                    return tools
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
                print(run_tools)
                results = self.onRunTools(run_tools)
                if isinstance(results, Response):
                    return results
                json_results = run_tools_to_json(results)
                return Response(json_results, content_type='application/json')
            else:
                raise Exception("No data provided")
        except Exception as e:
            print(e)
            return Response("No data provided", content_type='application/json')

    def get_devices(self, req: Request) -> Response:
        try:
            json_data = req.get_json(force=True, silent=True)
            if json_data:
                get_devices: List[str] = json_data
                devices = self.onGetDevices(get_devices)
                if isinstance(devices, Response):
                    return devices
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