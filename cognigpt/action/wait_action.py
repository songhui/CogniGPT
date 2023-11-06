from .basic_action import BasicAction
from time import sleep

class WaitAction(BasicAction):

    def is_ready(self):
        return False
    
    def _exec(self, message):
        while True:
            if self.is_ready():
                print('not ready')
                break
            print('slept')
            sleep(1)
        return message
                

if __name__ == '__main__':
    action = WaitAction()
    action.run({'type':'command', 'content': 'nothing'})