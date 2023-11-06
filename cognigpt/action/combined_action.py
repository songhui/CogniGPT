from .basic_action import BasicAction

class IF(BasicAction):
    def __init__(self, condition, action, else_action = None):
        self.condition = condition
        self.action = action
        self.else_action = else_action
        super().__init__()

    def run(self, message):
        action = None
        if self.condition(self, message):
            action = self.action     
        else:
            action = self.else_action
        if action:
            message = message.copy()
            action.process = self.process
            return action.run(message)
        else:
            return message
    
    def traverse(self, fn):
        if self.action:
            self.action.traverse(fn)
        if self.else_action:
            self.else_action.traverse(fn)

        return super().traverse(fn)
    
class SEQ(BasicAction):
    def __init__(self, body=[]):
        self.body = body
        super().__init__()

    def run(self, message):
        message = message.copy()
        print('---')
        print(message)
        for item in self.body:
            item.process = self.process
            message = item.run(message)
            # print(message)
        return super().run(message)
    
    def traverse(self, fn):
        for act in self.body:
            act.traverse(fn)
        return super().traverse(fn)
