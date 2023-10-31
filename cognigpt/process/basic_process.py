from ..action.basic_action import PrintMessageAction
from ..attention.basic_attention import BasicAttention


class IgnoreFrom(BasicAttention):
    def __init__(self, froms: []):
        self.excluded = froms

    def relevant(self, message) -> bool:
        if not 'from' in message:
            return True
        return not(message['from'] in self.excluded)

class BasicProcess:
    def __init__(self, name, actions: {}, attentions: []):
        self.name = name
        self.actions = actions
        self.attentions = attentions

    def receive(self, message):
        for att in self.attentions:
            if not att.relevant(message):
                return
        for i in self.actions:
            self.actions[i].run(message)

    def get_responser(self):
        return PrintMessageAction()
    
    def add_actions(self, name, unit):
        self.actions[name] = unit