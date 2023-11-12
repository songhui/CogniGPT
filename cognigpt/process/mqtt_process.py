import paho.mqtt.client as mqtt
import json
from threading import Thread

from cognigpt.gws.message import MessageType

from ..action.combined_action import SEQ

from .basic_process import BasicProcess, IgnoreFrom
from ..action.basic_action import BasicAction, AppendAction
from ..attention.basic_attention import BasicAttention



class MQTTProcess(BasicProcess):

    def __init__(self, name, mqttbroker, actions: {}, attentions: []):
        self.mqttbroker = mqttbroker
        super().__init__(name, actions, attentions)

    def start(self, message={}, variables={}):

        super().start(message, variables)
        self.listen()

    def listen(self):
        
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))
            client.subscribe(self.mqttbroker['topic'])
        
        def on_message(client, userdata, msg):
            # print(msg.topic+" "+str(msg.payload))
            message = json.loads(msg.payload)
            thread = Thread(target=self.receive, args=[message])
            thread.start()
            # self.receive(message)
            
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.mqttbroker['host'], self.mqttbroker['port'], 60)
        client.loop_forever()


class NotFromMeAttention(BasicAttention):
    
    def relevant(self, message) -> bool:
        # print('------------' + message['from'] + '---' + self.process.name + '---')
        if ('from' in message) and (self.process) and (message['from'] == self.process.name):
            return False
        return True


class MQTTResponserAction(BasicAction):
    def __init__(self, subseq={}, attentions=[]):
        self.client = mqtt.Client()
        super().__init__()

    def run(self, message):
        message['from'] = self.process.name
        try:
            mqttbroker = self.process.mqttbroker
            if not self.client.is_connected():
                self.client.connect(mqttbroker['host'], mqttbroker['port'])
            # self.client.on_publish()
            self.client.publish(mqttbroker['topic'], json.dumps(message))
            return message  
        except Exception as e:
            print(e)
            return message

if __name__ == '__main__':
    process_name = 'NoOne'
    process = MQTTProcess(
        process_name, 
        mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'some/topic'},
        actions={'single': SEQ([AppendAction('-by my self'), MQTTResponserAction()])}, 
        attentions=[NotFromMeAttention()]
    )
    
    process.init_all_actions()
    process.listen()

    # Test this with ```mqtt pub -h 'localhost' -t 'some/topic' -m '{"type":"text", "from":"host", "content":"hello"}' ````