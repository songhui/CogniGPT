from enum import auto
from strenum import StrEnum

class MessageType(StrEnum):
    DYNABIC_CODE = auto()


class BasicAction:
    def __init__(self, follow_ups = {}):
        self.follow_ups = follow_ups.copy()

    def run(self, message):
        for i in self.follow_ups:
            self.follow_ups[i].run(message)



if __name__ == "__main__":
    None