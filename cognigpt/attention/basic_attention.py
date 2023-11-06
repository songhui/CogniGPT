import random
random.seed()

from ..action.basic_action import MessageType

class BasicAttention:
    def __init__(self):
        self.process = None
    def relevant(self, message) -> bool:
        return False

class ProbabilityAttention:
    def _relevance(self, message) -> float:
        return 0
    
    def is_relevant(self, message) -> bool:
        relevance = self._relevance(message)
        return random.random() < relevance
    
class AlwaysAttention(BasicAttention):
    def relevant(self, message):
        return True
    
class MessageFromAttention(BasicAttention):
    def __init__(self, included=[]):
        self.included = included
        super().__init__()

    def relevant(self, message):
        if ('from' in message) and (message['from'] in self.included):
            return True
        return False
            
class MessageLambdaAttention(BasicAttention):
    def __init__(self, message_lambda):
        self.message_lambda = message_lambda

    def relevant(self, message):
        return self.message_lambda(message)
    
class MessageContentLambdaAttention(BasicAttention):
    def __init__(self, message_content_lambda):
        self.message_content_lambda = message_content_lambda

    def relevant(self, message):
        return self.message_content_lambda(message['content'])

if __name__ == '__main__':

    from ..action.basic_action import PrintMessageAction




