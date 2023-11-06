from .basic_action import BasicAction

class IF(BasicAction):
    def __init__(self, condition, action, else_action = None):
        self.condition = condition
        self.action = action
        self.else_action = else_action
        super().__init__(subseq={}, attention=[])

    def _exec(self, message):
        action = None
        if self.condition(self, message):
            action = self.action     
        else:
            action = self.else_action
        if action:
            message = message.copy()
            action.process = self.process
            return action._exec(message)
        else:
            return message


class ConditionalAction(BasicAction):
    def __init__(self, condition, body = [], subseq={}, attention=[]):
        self.condition = condition
        self.body = body
        super().__init__(subseq, attention)
    def _exec(self, message):
        message_copy = message.copy()
        if self.condition(self.process, message):
            for act in self.body:
                message_copy = act._exec(message_copy)
        return super()._exec(message)
    
class SEQ(BasicAction):
    def __init__(self, body=[]):
        self.body = body
        super().__init__({}, [])

    def _exec(self, message):
        message = message.copy()
        for item in self.body:
            item.process = self.process
            message = item._exec(message)
            # print(message)
        return super()._exec(message)
