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
        self.variables = {}

    def receive(self, message):
        for att in self.attentions:
            if not att.relevant(message):
                return
        for i in self.actions:
            self.actions[i].run(message)
    
    def add_actions(self, name, action):
        self.actions[name] = action
    


    def init_all_actions(self):
        def set_process(act):
            act.process = self
        for i in self.actions:
            self.actions[i].traverse(set_process)
        for att in self.attentions:
            att.process = self


if __name__ == '__main__':
    
    process = BasicProcess('pname', {'acc': PrintMessageAction()}, [])
    process.init_all_actions()


