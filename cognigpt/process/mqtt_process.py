import paho.mqtt.client as mqtt
import json

from .basic_process import BasicProcess, IgnoreFrom
from ..action.basic_action import BasicAction, AppendAction



class MQTTProcess(BasicProcess):

    class MQTTResponserAction(BasicAction):
        def __init__(self, process, follow_ups={}):
            self.process_name = process.name
            self.mqttbroker = process.mqttbroker
            self.client = mqtt.Client()
            super().__init__(follow_ups)
            
        def _exec(self, message):
            message['from'] = self.process_name
            if not self.client.is_connected():
                self.client.connect(self.mqttbroker['host'], self.mqttbroker['port'])
            # self.client.on_publish()
            self.client.publish(self.mqttbroker['topic'], json.dumps(message))
            return message      

    def __init__(self, name, mqttbroker, units: {}, attentions: []):
        self.mqttbroker = mqttbroker
        super().__init__(name, units, attentions)

    def get_responser(self):
        return self.MQTTResponserAction(self)
    
    def listen(self):
        
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))
            client.subscribe(self.mqttbroker['topic'])
        
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
            message = json.loads(msg.payload)
            self.receive(message)
            
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.mqttbroker['host'], self.mqttbroker['port'], 60)
        client.loop_forever()

        



if __name__ == '__main__':
    process_name = 'NoOne'
    process = MQTTProcess(process_name, 
                          mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'some/topic'},
                          units={}, 
                          attentions=[IgnoreFrom([process_name], {})]
                          )
    
    responser = process.get_responser()
    append_action = AppendAction(postfix = '- by myself', follow_ups = {'publish': responser})
    process.add_units('test', append_action)
    process.listen()