from .basic_action import BasicAction

class CliInputAction(BasicAction):
    def _exec(self, message):
        prompt = input("user input: ")
        message['content'] = prompt
        return message
        