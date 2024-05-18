def run_all_function(functions: list[RunFunction], isEvaluation: bool = False) -> list[FunctionResult]:
   if functions:
      results = []
      for function in functions:
         print(function.to_json())
         argJson = json.loads(function.arguments)
         if function.name == "set_led":
            try:
               ledName =  argJson["name"]
               value = argJson["value"]
               if isEvaluation == False:
                  set_led(ledName, value)
               functionCall = FunctionResult(name=function.name, result="LED is now " + value)
               results.append(functionCall)
            except Exception as e:
               functionCall = FunctionResult(name=function.name, result="Couldn't toggle LED, because " + str(e))
               results.append(functionCall)
         elif function.name == "print_lcd":
            try:
               text = argJson["text"]
               if isEvaluation == False:
                  print_lcd(text)
               functionCall = FunctionResult(name=function.name, result="LCD is now " + text)
               results.append(functionCall)
            except Exception as e:
               functionCall = FunctionResult(name=function.name, result="Couldn't write to LCD, because " + str(e))
               results.append(functionCall)
         elif function.name == "capture_image":
            try:
               url = "https://st3.depositphotos.com/12760300/35102/i/450/depositphotos_351021910-stock-photo-close-computer-green-microcircuits-lie.jpg"
               if isEvaluation == False:
                  url = capture_image()
               functionCall = FunctionResult(name=function.name, result="ONLY inform the user that the image is successfully captured", ui="image", data=url)
               results.append(functionCall)
            except Exception as e:
               functionCall = FunctionResult(name=function.name, result="Couldn't capture the image because " + str(e))
               results.append(functionCall)
         elif function.name == "get_raspberry_stats":
            stats = get_raspberry_stats()
            functionCall = FunctionResult(name=function.name, result="Inform the user that the CPU, RAM, disk and uptime has been extracted, DON'T mention any values", ui="table", data=stats)
            results.append(functionCall)
         elif function.name == "get_recorded__sensor_data":
            sensorNames = argJson["sensorNames"]
            interval = argJson["interval"]
            data: DataPlot = get_recorded__sensor_data(sensorNames, interval)
            functionCall = FunctionResult(name=function.name, result="ONLY inform the user that the data and plot is shown and that is it, I repeat do not mention anything else", ui="plot", data=data.to_json())
            results.append(functionCall)
         elif function.name == "get_connected_devices":
            deviceNames = argJson["deviceNames"]
            devices: List[Device] = get_connected_devices(deviceNames)
            arrayString = [device.to_json() for device in devices]
            values = json.dumps([device.to_llm_output() for device in devices])
            functionCall = FunctionResult(name=function.name, result="Here are the fetced devices: "+values+" this will be shown to the user in the UI above, so ONLY inform the user that the devices are shown above and thats it!", ui="cards", data=arrayString)
            results.append(functionCall)
         elif function.name == "get_location":
            location = get_location()
            functionCall = FunctionResult(name=function.name, result="Extracted the coordinates from the connected GPS the module, inform the user that a map will be shown above and thats it", ui="map", data=location.to_json())
            results.append(functionCall)
         elif function.name == "set_servo_angles":
            try:
               angles = argJson["angles"]
               output = ""
               if isEvaluation == False:
                  output = set_servo_angles(angles)
               functionCall = FunctionResult(name=function.name, result="Servo has been set to the given angles", data=output)
               results.append(functionCall)
            except Exception as e:
               functionCall = FunctionResult(name=function.name, result="Couldn't set the servo angles because " + str(e))
               results.append(functionCall)
         elif function.name == "set_fan":
            try:
               value = argJson["value"]
               if isEvaluation == False:
                  set_fan(value)
               functionCall = FunctionResult(name=function.name, result="Fan is now " + value)
               results.append(functionCall)
            except Exception as e:
               functionCall = FunctionResult(name=function.name, result="Couldn't set the fan because " + str(e))
               results.append(functionCall)
      return results
   return []
