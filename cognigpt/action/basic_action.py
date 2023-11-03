from enum import auto
from strenum import StrEnum
from ..gws.message import MessageType, terminate_message

class BasicAction:
    def __init__(self, subseq = {}, attention = []):
        self.subseq = subseq.copy()
        self.attention = attention.copy()

    def _exec(self, message):
        return terminate_message()

    def run(self, message):
        for att in self.attention:
            if not att.relevant():
                return 
        new_message = self._exec(message)
        if new_message['type'] == MessageType.TERMINATE:
            return
        for i in self.subseq:
            self.subseq[i].run(new_message)
    def set_process(self, process):
        self.process = process

class PrintMessageAction(BasicAction):
    def _exec(self, message):
        print(message)
        return message
    
class AppendAction(BasicAction):
    def __init__(self, postfix, subseq: {}):
        self.postfix = postfix
        super().__init__(subseq)

    def _exec(self, message):
        message['content'] = message['content'] + self.postfix
        return message

if __name__ == "__main__":
    None

