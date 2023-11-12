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
                 she or her guests need to do. Every task must be assigned to one and only one person. 
                 After you knows the tasks, please send a message to the guest group,
                 ask them if they have some constraints or preferences for the tasks. After you
                 get enough responses, you can make an assignment to the guests and the host
                 herself, and send a simple message with pairs of Person -> Task.
                 All generated text should be short - no need for explanation or being polite.
                 Use common sense for task dependencies
                 Whenever you need more information from the host, 
                 you say "To Host", followed by your question.
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

    # host reply: Buy food, use the food to make meal, buy drinks. I don't like cooking, btw.

