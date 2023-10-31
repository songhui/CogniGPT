import random
random.seed()

from ..action.basic_action import MessageType

class BasicAttention:
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
            

if __name__ == '__main__':

    from ..action.basic_action import PrintMessageAction

    attention = AlwaysAttention({'opration': PrintMessageAction()})
    attention.run({'type':'any', 'content': 'my content'})


