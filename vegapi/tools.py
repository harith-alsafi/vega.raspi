import inspect
import json
from typing import Callable, List

class Parameter:
    name: str
    description: str
    param_type: str
    enum: List[str]
    is_optional: bool

    def __init__(self, name: str, description: str, param_type: str, is_optional: bool = False, enum: list[str] = []):
        if param_type == "list":
            self.param_type = "array"
        elif param_type == "str":
            self.param_type = "string"
        self.name = name
        self.description = description
        self.enum = enum
        self.is_optional = is_optional

    def to_dict(self):  
        return {
            'description': self.description,
            'type': self.param_type,
            **({'enum': self.enum} if self.enum else {}) 
        }

class Tool:
    return_type: str
    name: str
    description: str
    parameters: List[Parameter]
    function: Callable

    def __init__(self, name: str, description: str, function: Callable, return_type:str = None, parameters: list[Parameter] = []):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
        self.return_type = return_type

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def to_dict(self):  
        parameters = {
            "type": "object",
            **({'properties': {param.name: param.to_dict() for param in self.parameters}} if len(self.parameters) > 0 else {}),
            **({'return': self.return_type} if self.return_type else {}),
            **({'required':  [param.name for param in self.parameters if not param.is_optional]} if len(self.parameters) > 0 and any(obj.is_optional is False for obj in self.parameters) else {}),
        }
        return {
            "name": self.name,
            "description": self.description,
            **({'parameters': parameters} if len(self.parameters) > 0 or self.return_type is not "_empty" else {}) 
        }

def tools_to_json(tools: List[Tool]):
    return json.dumps([tool.to_dict() for tool in tools], indent=4)

class VegaTools:
    tools: List[Tool]

    def __init__(self):
        self.tools = []

    def add_tool(self, description:str, parameter_description: dict[str, str]=None, return_type:str=None, name:str=None):
        def decorator(func: Callable):
            signature = inspect.signature(func)
            parameters = signature.parameters

            nonlocal return_type
            if return_type is None:
                return_type = signature.return_annotation.__name__
            
            nonlocal name
            if name is None:
                name = func.__name__

            nonlocal parameter_description
            actual_parameters: list[Parameter]  = []
            for param in parameters:
                param_info = parameters[param]
                actual_parameters.append(Parameter(param,  parameter_description.get(param, ""), param_info.annotation.__name__, param_info.default != param_info.empty))

            tool = Tool(name, description, func, return_type, actual_parameters)
            self.tools.append(tool)
            return func
        return decorator
    
    def to_json(self):
        return tools_to_json(self.tools)