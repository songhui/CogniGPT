from enum import auto
from strenum import StrEnum
from ..gws.message import MessageType, terminate_message

class BasicAction:
    def __init__(self):
        self.process = None

    def run(self, message):
        return message

    def set_process(self, process):
        self.process = process

    def traverse(self, fun):
        fun(self)
        None

class PrintMessageAction(BasicAction):
    def run(self, message):
        print(message)
        return message
    
class AppendAction(BasicAction):
    def __init__(self, postfix):
        self.postfix = postfix
        super().__init__()

    def run(self, message):
        message = message.copy()
        message['content'] = message['content'] + self.postfix
        return message

class MessageUpdateAction(BasicAction):
    def __init__(self, update:dict = {}):
        self.update = update
        super().__init__()

    def run(self, message):
        message = message.copy()
        message.update(self.update)
        return super().run(message)

if __name__ == "__main__":
    None

