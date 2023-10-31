from enum import auto
from strenum import StrEnum
from ..gws.message import MessageType, terminate_message




class BasicAction:
    def __init__(self, follow_ups = {}):
        self.follow_ups = follow_ups.copy()

    def _exec(self, message):
        return terminate_message()

    def run(self, message):
        new_message = self._exec(message)
        if new_message['type'] == MessageType.TERMINATE:
            return
        for i in self.follow_ups:
            self.follow_ups[i].run(message)

class PrintMessageAction(BasicAction):
    def _exec(self, message):
        print(message)
        return message
    
class AppendAction(BasicAction):
    def __init__(self, postfix, follow_ups: {}):
        self.postfix = postfix
        super().__init__(follow_ups)

    def _exec(self, message):
        message['content'] = message['content'] + self.postfix
        return message

if __name__ == "__main__":
    None

