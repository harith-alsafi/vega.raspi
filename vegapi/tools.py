import inspect
import json

class Parameter:
    name: str
    description: str
    param_type: str
    enum: list[str]
    is_optional: bool

    def __init__(self, name: str, description: str, param_type: str, is_optional: bool = False, enum: list[str] = []):
        self.name = name
        self.description = description
        self.param_type = param_type
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
    parameters: list[Parameter]
    function: callable

    def __init__(self, name: str, description: str, function: callable, return_type:str = None, parameters: list[Parameter] = []):
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
            **({'parameters': parameters} if len(self.parameters) > 0 or self.return_type is not None else {}) 
        }

class VegaTools:
    tools: list[Tool]

    def __init__(self):
        self.tools = []
        self.functions = []

    def add_tool(self, description:str, parameter_description: dict[str, str], return_type:str=None, name:str=None):
        def decorator(func: callable):
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
        return json.dumps([tool.to_dict() for tool in self.tools], indent=4)
