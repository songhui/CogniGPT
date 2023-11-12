from threading import Thread
from ..gws.message import MessageType
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
        for i in self.normal_actions():
            self.actions[i].run(message)
    
    def add_actions(self, name, action):
        self.actions[name] = action
    
    def normal_actions(self):
        return [x for x in self.actions if not x.startswith("_")]

    def init_all_actions(self):
        def set_process(act):
            act.process = self
        for i in self.actions:
            self.actions[i].traverse(set_process)
        for att in self.attentions:
            att.process = self
    
    def start(self, message:dict={}, variables:dict={}):
        if not message:
            message = {'type': MessageType.SYSTEM, 'content': ''}
        if variables:
            self.variables.update(variables)
        self.init_all_actions()
        if '_init' in self.actions:
            thread = Thread(target=self.actions['_init'].run, args=[message])
            thread.start()



if __name__ == '__main__':
    
    process = BasicProcess('pname', {'acc': PrintMessageAction()}, [])
    process.init_all_actions()


