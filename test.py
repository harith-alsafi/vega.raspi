from typing import Optional
from vegapi import VegaTools, Tool, Parameter, VegaApi
import signal

vega_tools = VegaTools()

@vega_tools.add_tool(description="Test function", parameter_description={"a": "First number", "b": "Second number", "c": "Third number"})
def test_function(a: int, b: int, c:int = 3) -> int:
    return a + b

def get_tools(str: Optional[str] = None):
    return vega_tools.tools

def signal_handler(signum, frame):
    print('Received signal to terminate')
    # Perform cleanup or shutdown tasks here
    # ...

    # Exit the program
    import sys
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

api: VegaApi = VegaApi(onGetFunctions=get_tools)
api.run()

print(vega_tools.to_json())


while True:
    print("Running...")
    import time
    time.sleep(1)
