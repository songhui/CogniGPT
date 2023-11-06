from .basic_action import BasicAction, PrintMessageAction
from .wait_action import WaitAction
from ..gpt.api import call_with_context
from ..gws.message import MessageType

class GptAction(BasicAction):
    def __init__(self, subseq = {}, attention = []):
        self.context = []
        super().__init__(subseq, attention)

    def add_context(self, role: str, content: str):
        self.context.append({'role': role, 'content': content})

    def _exec(self, message):
        role = 'user'
        answer = call_with_context(self.context, message['content'], role)
        return {
            'type': MessageType.TEXT,
            'content': answer
        }

class GptActionWithResponse(GptAction):
    def _exec(self, message):
        if not 'responses' in self.process.variables:
            self.process.variables['responses'] = []
        responses = self.process.variables['responses']
        for res in responses:
            self.add_context(res['role'], res['content'])
        return super()._exec(message)

class CollectResponseAction(BasicAction):
    def _exec(self, message):
        variables = self.process.variables
        if not 'responses' in variables:
            variables['responses'] = []
        new_content = "['{}' replied] {}".format(message['from'], message['content'])
        variables['responses'].append({'role': 'user', 'content': new_content})  
        return message   

if __name__ == "__main__":
    action = GptAction({'print': PrintMessageAction()}, [])
    while True:
        prompt = input('promt: ')
        action.run({'type': MessageType.TEXT, 'content': prompt})
