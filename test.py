from typing import Optional

from flask import Flask
from vegapi import VegaTools, Tool, Parameter, VegaApi
import signal


vega_tools = VegaTools()

@vega_tools.add_tool(description="Test function", parameter_description={"a": "First number", "b": "Second number", "c": "Third number"})
def test_function(a: int, b: int, c:int = 3) -> int:
    return a + b

def get_tools(str: Optional[str] = None):
    return vega_tools.tools




api: VegaApi = VegaApi(onGetFunctions=get_tools)
api.run_flask_app()




while True:
    # print("Running...")
    import time
    time.sleep(1)
