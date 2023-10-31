from ..action.basic_action import PrintMessageAction
from ..attention.basic_attention import BasicAttention


class IgnoreFrom(BasicAttention):
    def __init__(self, froms: [], follow_ups: {}):
        self.excluded = froms
        super().__init__(follow_ups)

    def is_relevant(self, message) -> bool:
        if not 'from' in message:
            return True
        return not(message['from'] in self.excluded)

class BasicProcess:
    def __init__(self, name, units: {}, attentions: []):
        self.name = name
        self.units = units
        self.attentions = attentions

    def receive(self, message):
        for att in self.attentions:
            if not att.is_relevant(message):
                return
        for i in self.units:
            self.units[i].run(message)

    def get_responser(self):
        return PrintMessageAction()
    
    def add_units(self, name, unit):
        self.units[name] = unit