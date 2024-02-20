from vegapi.tools import VegaTools, Tool, Parameter

vega_tools = VegaTools()

@vega_tools.add_tool(description="Test function", parameter_description={"a": "First number", "b": "Second number", "c": "Third number"})
def test_function(a: int, b: int, c:int = 3) -> int:
    return a + b

print(vega_tools.to_json())