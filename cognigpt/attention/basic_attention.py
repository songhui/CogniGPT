import random
random.seed()

from ..action.basic_action import MessageType

class BasicAttention:
    def __init__(self, follow_ups: {}):
        self.follow_ups = follow_ups

    def _relevance(self, message) -> float:
        return 0
    
    def run(self, message):
        relevance = self._relevance(message)
        if random.random() < relevance:
            for i in self.follow_ups:
                self.follow_ups[i].run(message)
    
    def is_relevant(self, message) -> bool:
        relevance = self._relevance(message)
        return random.random() < relevance
    


class AlwaysAttention(BasicAttention):

    def _relevance(self, message):
        return 1
            

if __name__ == '__main__':

    from ..action.basic_action import PrintMessageAction

    attention = AlwaysAttention({'opration': PrintMessageAction()})
    attention.run({'type':'any', 'content': 'my content'})


