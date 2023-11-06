from cognigpt.action.gpt_action import GptAction, GptActionWithResponse, CollectResponseAction
from cognigpt.attention.basic_attention import BasicAttention, MessageFromAttention
from cognigpt.process.mqtt_process import MQTTProcess, MQTTResponserAction, NotFromMeAttention
from cognigpt.action.cli_action import CliInputAction
from cognigpt.action.combined_action import SEQ, IF

if __name__ == '__main__':
    name = input('Your name: ')
    mqttbroker = {'host': 'localhost', 'port': 1883, 'topic': 'cognigpt/dinner-party'}
    process = MQTTProcess(
        name, 
        mqttbroker=mqttbroker, 
        actions={'main': SEQ([CliInputAction(), MQTTResponserAction()])},
        attentions=[NotFromMeAttention(), MessageFromAttention(['host'])])
    process.init_all_actions()
    process.listen()