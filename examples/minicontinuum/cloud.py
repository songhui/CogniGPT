

import json
from cognigpt.action.basic_action import BasicAction, PrintMessageAction
from cognigpt.action.gpt_action import AddWhoSaidAction, GptAction, GptActionWithResponse, CollectResponseAction
from cognigpt.attention.basic_attention import BasicAttention
from cognigpt.gws.message import MessageType
from cognigpt.process.mqtt_process import MQTTProcess, MQTTResponserAction, NotFromMeAttention
from cognigpt.action.cli_action import CliInputAction
from cognigpt.action.combined_action import SEQ, IF, WHILE_TRUE
from cognigpt.gpt.api import generate_code



background = '''\
You are an assistent helping manage software services running on a cloud infrastructure. \
An edge cluster running together with the cloud. \
A service named DataAnalytics has several instances running on \
either the cloud, the edge, or both. 
Variables: minimal total number of instances for DataAnalytics \
(variable name: min_inst), the current number of instances on the cloud (name: cloud_inst), \
and the current number of instances on the edge (name: edge_inst) \
The cloud can host maximal 15 instances with low cost. when it hosts 16-30 instances, the cost is high. \
We assume running more or less instances on edge does not affect the cost. \
In each round of adaptation, you will try to adjust the number of instances on the cloud and on \
the edge, considering the cost and the performance. \
Should you see the need to adapt, your output (very short) will a json document in the following structure: \
{
  "EdgeInst": "<number of instances you ask the edge to host>",
  "CloudInst": "<number of instances needed to host on the cloud>",
  "Explanation": "a short explanation of your decision (no more than 25 tokens)"
}\
If you don't see the need to adapt, just return {"message": "No Change"}
The edge may reject your suggestion, and then you will receive a response with several alternatives. \
In the following round of adaptation, you could consider picking one of these alternatives to give another try.
'''

CODE_REQ='''
Only the user knows how many instances of the service are needed. \
The value is in a file at "./examples/minicontinuum/cusvar.txt", and the content \
of that file is only a number, which is value of instances. \
The function should return a dict: {"min_inst": <the value from the file>}
'''

class UiAction(BasicAction):
    def __init__(self, gpt_action, mqtt_resonser):
        self.gpt_action = gpt_action
        self.mqtt_responser = mqtt_resonser

    def traverse(self, fun):
        self.gpt_action.traverse(fun)
        self.mqtt_responser.traverse(fun)
        return super().traverse(fun)

    def run(self, message):
        prompt = ""
        usrinput = input('Input: chvar (<var_name>=<var_value>, )* | intent <user intent> | [Nothing, just press Enter]\n')
        if usrinput.startswith('chvar'):
            for varval in usrinput[5:].split(','):
                [var, val] = varval.split('=')
                self.process.variables[var.strip()] = val.strip()
        elif usrinput.startswith('intent'):
            prompt = prompt + "New intent from system operator: " + usrinput[7:]
        elif usrinput.startswith('query'):
            self.mqtt_responser.run({'to': 'customer', 'type': MessageType.QUERY, 'content':''})
            return super().run(message)
        else:
            None
        
        variables = self.process.variables
        vdict = {k: variables[k] for k in ('min_inst', 'cloud_inst', 'edge_inst')}
        variables['responses'].append({'role': 'user', 'content': json.dumps(vdict)})

        answer = self.gpt_action.run({'type': MessageType.TEXT, 'from': 'cloud', 'content': prompt})
        print(answer['content'])
        content = json.loads(answer['content'])
        if ('message' in content) and (content['message'] == 'No Change'):
            None
        else:
            out_message = message.copy()
            edge_inst = content['EdgeInst']
            out_message.update({
                'content': "Cloud suggests edge instance: " + edge_inst,
                'to': 'edge',
                'type': MessageType.TEXT
            })

            self.mqtt_responser.run(out_message)
            print("Message sent to edge. Suggested edge instances: " + edge_inst)
                
            cloud_inst = content['CloudInst']
            self.process.variables['cloud_inst'] = cloud_inst
            print("Number of cloud instance updated: " + cloud_inst)

            print(content['Explanation'])

        return super().run(message)
    
class CollectEdgeResponse(CollectResponseAction):
    def run(self, message):
        try:
            content = json.loads(message['content'])
            if 'edge_inst' in content:
                self.process.variables.update({'edge_inst': content['edge_inst']})
            elif 'min_inst' in content:
                self.process.variables.update({'min_inst': content['min_inst']})
            print('updated variables: {}'.format(self.process.variables))
            
        except Exception as e:
            # print(e)
            # print('return not in json')
            print(message)
            if message.get('from') == 'operator':
                intent = message['content']
                message['content'] = "Operator's intent: ${}".format(intent)

        if message.get('from') in ('edge', 'operator'): # do not consider customer's query as response
            super().run(message)
    
class PopulateCode(BasicAction):
    def run(self, message):
        print(CODE_REQ)
        code = generate_code(CODE_REQ)
        print(code)
        message = {
            "to": "customer",
            "type": MessageType.DYNAMIC_CODE,
            "content": code
        }
        return super().run(message)

if __name__ == '__main__':
    gpt_act = GptActionWithResponse()
    gpt_act.add_context('system', background)
    mqtt_responser = MQTTResponserAction()
    ui_act = UiAction(gpt_act, mqtt_responser)

    populate_code = PopulateCode()


    process = MQTTProcess(
        name='cloud', 
        mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'cognigpt/dinner-party'},
        actions={
            '_init': SEQ([populate_code, mqtt_responser, WHILE_TRUE(ui_act)]),
            'connect_response': CollectEdgeResponse()
        },
        attentions=[NotFromMeAttention()]
    )



    process.start(
        message={}, 
        variables={'min_inst': '20', 'cloud_inst': '10', 'edge_inst': 10, 'responses': []}
    )




