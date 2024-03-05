from typing import Callable, List, Optional
from vegapi.api import RunTool, ToolResult, VegaApi
from vegapi.database import DataSeries, Database
from vegapi.devices import Device
from vegapi.tools import VegaTools, Tool, Parameter, tools_to_json

class Vega(VegaTools, VegaApi, Database):
    devices: List[Device]
    def __init__(self, onRunTools: Callable[[list[RunTool]], list[ToolResult]], onGetDevices: Callable[[Optional[list[str]]], list[Device]], onEveryPeriod: Callable[[], List[DataSeries]], period: int = 2):
        VegaTools.__init__(self)
        VegaApi.__init__(self, onGetTools=self.on_get_tools, onRunTools=onRunTools, onGetDevices=onGetDevices)
        Database.__init__(self, onEveryPeriod=onEveryPeriod, period=period)
        self.devices = []

    def on_get_tools(self, names: Optional[List[str]] = None):
        if names and names != []:
            return [tool for tool in self.tools if tool.name in names]
        return self.tools
    
    def add_device(self, device: Device):
        self.devices.append(device)


