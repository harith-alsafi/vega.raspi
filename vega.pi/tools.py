import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[
       {"role": "user", "content": "Explain how to assemble a PC"}
    ],
    functions=[
        {
          "name": "get_answer_for_user_query",
          "description": "Get user answer in series of steps",
        }
    ],
    function_call="auto"
)

class VegaTools:
    def __init__(self):
        self._pi = pigpio.pi()

    def set_gpio(self, gpio, value):
        self._pi.write(gpio, value)

    def get_gpio(self, gpio):
        return self._pi.read(gpio)

    def cleanup(self):
        self._pi.stop()