import paho.mqtt.client as mqtt

class BasicProcess:
    def __init__(self, name, units: {}):
        self.name = name
        self.units = units

    def receive(self, message):
        for i in self.units:
            self.units[i].run(message)

class MQTTProcess(BasicProcess):

    def listen_to(self, host, port, topic):
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))
            client.subscribe(topic)
        
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(host, port, 60)
        client.loop_forever()



if __name__ == '__main__':
    process = MQTTProcess('noone', {})
    process.listen_to('broker.hivemq.com', 1883, '*')