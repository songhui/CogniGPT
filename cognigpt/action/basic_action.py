from enum import auto
from strenum import StrEnum

class MessageType:
    DYNABIC_CODE = 'dynabic_code'
    COMMAND = 'command'
    TERMINATE = 'terminate'
    RETURN = 'return'

def terminate_message():
    return {'type': MessageType.TERMINATE, 'content': ''}  

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

if __name__ == "__main__":
    None