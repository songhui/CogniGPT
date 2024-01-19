from cognigpt.action.basic_action import BasicAction
from cognigpt.action.combined_action import SEQ, WHILE_TRUE
from cognigpt.process.mqtt_process import MQTTProcess, MQTTResponserAction, NotFromMeAttention
from termcolor import colored

class OperatorUiAction(BasicAction):
    def __init__(self, mqtt_resonser):
        self.mqtt_responser = mqtt_resonser

    def traverse(self, fun):
        self.mqtt_responser.traverse(fun)
        return super().traverse(fun)
    
    def run(self, message):
        prompt = input('Operator intent:')
        message ={
            "to": "all",
            "content": prompt
        }
        return super().run(message)

class PrintFeedbackAction(BasicAction):
    def run(self, message):
        print("{}: {}".format(colored(message['from'], 'blue'), message['content']))
        return super().run(message)

if __name__ == '__main__':
    
    mqtt_responser = MQTTResponserAction()
    ui_act = OperatorUiAction(mqtt_responser)

    process = MQTTProcess(
        name='operator', 
        mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'cognigpt/dinner-party'},
        actions={
            '_init': WHILE_TRUE(SEQ([ui_act, mqtt_responser])),
            'connect_response': PrintFeedbackAction()
        },
        attentions=[NotFromMeAttention()]
    )
    process.start(
        message={}, 
        variables={}
    )