from cognigpt.action.basic_action import PrintMessageAction
from cognigpt.action.gpt_action import AddWhoSaidAction, GptAction, GptActionWithResponse, CollectResponseAction
from cognigpt.attention.basic_attention import BasicAttention
from cognigpt.process.mqtt_process import MQTTProcess, MQTTResponserAction, NotFromMeAttention
from cognigpt.action.cli_action import CliInputAction
from cognigpt.action.combined_action import SEQ, IF

class TwoResponseAttention(BasicAttention):
    def relevant(self, message) -> bool:
        return len(self.process.variables('responses')) >= 2

background = ''' You are an assistent helping of a human host. The host wants 
                 to call for a dinner party, and she will tell you some tasks that 
                 she or her guests need to do. To simplify, each task needs 1 hour. 
                 After you knows the tasks, please send a message to the guest group,
                 inviting them for party and ask them if they could take some tasks (1 for each person), 
                 if they have some constraints or preferences for some tasks. After you
                 get enough responses, you can make an assignment to the guests and the host
                 herself. 
                 All generated text and messages should be short and concise - no need for 
                 sophisticated explanation.
                 She needs at least 2 guests.
                 Some tasks may depend on another task, this you need to use commen senses.
                 Whenever you feel that you need more information from the host, 
                 you say "To Host", followed by your question to the host.
                 If you want to send a message to the guests, say "To Guest", followed by the 
                 message.
                 Otherwise, if you don't need to do another, but only to wait for more response,
                 just say "To Wait"
                 '''

if __name__ == '__main__':


    gpt_action = GptActionWithResponse()
    gpt_action.add_context('system', background)
    def is_not_start(action, message):
        return 'from' in message
    def is_to_host(action, message):
        return message['content'].startswith('To Host')
    def is_to_guest(action, message):
        return message['content'].startswith('To') and (not message['content'].startswith('To Host')) and (not message['content'].startswith('To Wait'))

    combined_action = SEQ(
        [
            AddWhoSaidAction(),
            gpt_action,
            PrintMessageAction(),
            IF(is_to_host, SEQ([CliInputAction(), gpt_action, PrintMessageAction()])),
            IF(is_to_guest, MQTTResponserAction())
        ]
    )

    process = MQTTProcess(
        name='host', 
        mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'cognigpt/dinner-party'},
        actions={'main': combined_action},
        attentions=[NotFromMeAttention()]
    )

    process.init_all_actions()
    combined_action.run({'type': 'start', 'content': ''})

    process.listen()

    # host reply: Buy food, use the food to make meal, buy drinks. I don't want to cook.

