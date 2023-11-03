from .basic_action import BasicAction, PrintMessageAction
from ..gpt.api import call_with_context
from ..gws.message import MessageType

class GptAction(BasicAction):
    def __init__(self, role = 'user', subseq = {}, attention = []):
        self.context = []
        self.role = role
        super().__init__(subseq, attention)

    def add_context(self, role: str, content: str):
        self.context.append({'role': role, 'content': content})

    def _exec(self, message):
        answer = call_with_context(self.context, message['content'], self.role)
        print(answer)
        return {
            'type': MessageType.TEXT,
            'content': answer
        }
        

if __name__ == "__main__":
    action = GptAction('user', {'print': PrintMessageAction()}, [])
    while True:
        prompt = input('promt: ')
        action.run({'type': MessageType.TEXT, 'content': prompt})
