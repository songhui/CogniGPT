from cognigpt.action.cli_action import CliInputAction
from cognigpt.process.mqtt_process import MQTTProcess
from cognigpt.action.basic_action import PrintMessageAction

if __name__ == '__main__':
    uinput = CliInputAction()
    print_message = PrintMessageAction({'input': uinput})

    process = MQTTProcess('myname',
                          mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'some/topic'},
                          actions= {'main': print_message},
                          attentions=[]
                          )
    process.listen()


