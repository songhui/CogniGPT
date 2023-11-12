from cognigpt.action.basic_action import MessageUpdateAction
from cognigpt.action.code_action import CodeIncubator
from cognigpt.action.combined_action import SEQ
from cognigpt.attention.basic_attention import MessageTypeAttention
from cognigpt.gws.message import MessageType
from cognigpt.process.mqtt_process import MQTTProcess, MQTTResponserAction, NotFromMeAttention

if __name__ == "__main__":
    code = CodeIncubator()
    mqtt_response = MQTTResponserAction()
    decorate = MessageUpdateAction(update={'type':MessageType.RETURN, 'to': 'cloud'})

    process = MQTTProcess(
        name='customer', 
        mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'cognigpt/dinner-party'},
        actions={
            'react_to_cloud': SEQ([code, decorate, mqtt_response])
        },
        attentions=[NotFromMeAttention(), MessageTypeAttention([MessageType.DYNAMIC_CODE, MessageType.QUERY]) ]
    )

    process.start()