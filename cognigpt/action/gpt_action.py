from .basic_action import BasicAction, PrintMessageAction
from .wait_action import WaitAction
from ..gpt.api import call_with_context
from ..gws.message import MessageType

class GptAction(BasicAction):
    def __init__(self):
        self.context = []
        super().__init__()

    def add_context(self, role: str, content: str):
        self.context.append({'role': role, 'content': content})

    def run(self, message):
        role = 'user'
        answer = call_with_context(self.context, message['content'], role)
        message = message.copy()
        message.update({'type': MessageType.TEXT, 'content': answer})
        return message

class GptActionWithResponse(GptAction):
    def run(self, message):
        if not 'responses' in self.process.variables:
            self.process.variables['responses'] = []
        responses = self.process.variables['responses']
        for res in responses:
            self.add_context(res['role'], res['content'])
        self.process.variables['responses'].clear() # responses are now in the context, no need here
        return super().run(message)

class CollectResponseAction(BasicAction):
    def run(self, message):
        variables = self.process.variables
        if not 'responses' in variables:
            variables['responses'] = []
        new_content = "['{}' replied] {}".format(message['from'], message['content'])
        variables['responses'].append({'role': 'user', 'content': new_content})  
        return message   

class AddWhoSaidAction(BasicAction):
    def run(self, message):
        message = message.copy()
        if 'from' in message:
            message['content'] = "['{}' said] {}".format(message['from'], message['content'])
        return message

if __name__ == "__main__":
    action = GptAction()
    while True:
        prompt = input('promt: ')
        action.run({'type': MessageType.TEXT, 'content': prompt})
