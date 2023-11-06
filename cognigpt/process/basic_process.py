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

    def get_responser(self):
        return PrintMessageAction()
    
    def add_actions(self, name, action):
        self.actions[name] = action
    
    def _init_action(self, action):
        action.process = self
        for att in action.attention:
            att.process = self


    def init_all_actions(self):
        def traverse(action):
            self._init_action(action)
            for i in action.subseq:
                traverse(action.subseq[i])
        for i in self.actions:
            traverse(self.actions[i])
        for att in self.attentions:
            att.process = self


if __name__ == '__main__':
    action1 = PrintMessageAction()
    action2 = PrintMessageAction({'act': action1})
    process = BasicProcess('pname', {'acc': action2}, [])
    process.init_all_actions()

    print(action1.process.name)