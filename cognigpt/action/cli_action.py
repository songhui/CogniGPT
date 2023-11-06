from .basic_action import BasicAction

class CliInputAction(BasicAction):
    def run(self, message):
        prompt = input("user input: ")
        message['content'] = prompt
        return message
        