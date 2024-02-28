from typing import Optional

from flask import Flask
from vegapi import VegaTools, Tool, Parameter, VegaApi, Device

from vegapi import Vega, RunTool, DataSeriesResult, ToolResult

def get_devices(names: Optional[list[str]] = None) -> list[Device]:
    return [
        Device(name="device1", description="device1 description", value=True, pins=[0], device_type="digital", isInput=True,  frequency=0.0),
        Device(name="device2", description="device2 description", value=0.2, pins=[1], device_type="analog", isInput=False, frequency=0.0),
        Device(name="device3", description="device3 description", value=0.5, pins=[2], device_type="analog", isInput=False, frequency=0.0),
    ]

def run_tools(tools: list[RunTool]) -> list[ToolResult]:
    return [
        ToolResult(name=tool.name, result=str(tool.arguments), status=True) for tool in tools
    ]

vega = Vega(onGetDevices=get_devices, onRunTools=run_tools)

@vega.add_tool(
    description="Test function", 
    parameter_description={"a": "First number", "b": "Second number", "c": "Third number"}
)
def test_function(a: int, b: int, c:int = 3) -> int:
    return a + b

vega.run()


while True:
    # print("Running...")
    import time
    time.sleep(1)
