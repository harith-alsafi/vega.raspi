import random
from typing import Optional
from flask import Flask, send_file
from vegapi import VegaTools, Tool, Parameter, VegaApi, Device
from vegapi import Vega, RunTool, DataSeriesResult, ToolResult
from vegapi.database import DataSeries

def get_devices(names: Optional[list[str]] = None) -> list[Device]:
    return [
        Device(name="device1", description="device1 description", value=True, pins=["0"], device_type="digital", isInput=True,  frequency=0.0),
        Device(name="device2", description="device2 description", value=0.2, pins=["1"], device_type="analog", isInput=False, frequency=0.0),
        Device(name="device3", description="device3 description", value=0.5, pins=["2"], device_type="analog", isInput=False, frequency=0.0),
    ]

def run_tools(tools: list[RunTool]) -> list[ToolResult]:
    return [
        ToolResult(name=tool.name, result=str(tool.arguments)) for tool in tools
    ]

def every_period() -> list[DataSeries]:
    return [
        DataSeries(name="device1", y=str(random.randint(0, 2))),
        DataSeries(name="device2",  y=str(random.randint(1, 3))),
        DataSeries(name="device3", y=str(random.randint(2, 4))),
    ]

vega = Vega(onGetDevices=get_devices, onRunTools=run_tools, onEveryPeriod=every_period, period=2)

@vega.add_tool(
    description="Test function", 
    parameter_description={"a": "First number", "b": "Second number", "c": "Third number"}
)
def test_function(a: int, b: int, c:int = 3) -> int:
    return a + b

vega.run()
vega.start_recording()

while True:
    # print("Running...")
    import time
    time.sleep(1)
