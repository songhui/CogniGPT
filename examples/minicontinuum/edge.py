import json

from termcolor import colored

from cognigpt.action.basic_action import BasicAction
from cognigpt.action.gpt_action import GptAction, GptActionWithResponse, CollectResponseAction
from cognigpt.attention.basic_attention import BasicAttention, MessageFromAttention, MessageLambdaAttention, MessageToAttention
from cognigpt.gws.message import MessageType
from cognigpt.process.mqtt_process import MQTTProcess, MQTTResponserAction, NotFromMeAttention
from cognigpt.action.cli_action import CliInputAction
from cognigpt.action.combined_action import SEQ, IF, WHILE_TRUE

background = '''\
You are an assistent helping manage an edge cluser of local computing resources. \
There will serveral instances of a data analytics service (named DataAnalytics) running on the cluster. \
Two variables describe the status of the cluster: \
The capacity (variable name: edge_cap) is the absolute maximal number of instances that can run in the cluster. \
The current number of service instances (variable name: edge_inst) \
When edge_inst is lower than 50\% of edge_cap, the service performance is good, but after that, \
when edge_inst get closer to edge_cap, the service performance goes to slightly bad, bad, and very bad, gradually. \
The cloud may send you message to suggest you change the number of instances. \
If you feel comfortable to implement the change, just do it. Otherwise, do as much as you can, explain why, and provide 1-3 
alternatives with number of edge instances and the potential performance. \
You response is a JSON document in the following structure: \
{
    "command": <a Kubernetes command to change the number of instances. If no change, leave it blank.>, 
    "edge_inst": <the number of instances after the change.>, \
    "performance": <the expected performance of the service after the change, in less than 5 tokens>, 
    "excuse": <short explanation (less than 15 tokens) about why you could not reach the suggested change.>,
    "alternatives": [{"edge_inst": <number of instances>, "performance": <consequence of performance under this number}, ...]
}
'''

class EdgeUiAction(BasicAction):
    def __init__(self, gpt_action, mqtt_resonser):
        self.gpt_action = gpt_action
        self.mqtt_responser = mqtt_resonser

    def traverse(self, fun):
        self.gpt_action.traverse(fun)
        self.mqtt_responser.traverse(fun)
        return super().traverse(fun)

    def run(self, message):
        prompt = ""
        usrinput = input('Input: chvar (<var_name>=<var_value>, )* | intent <user intent> | cloud <suggest inst> | [Nothing, just press Enter]\n')
        if usrinput.startswith('chvar'):
            for varval in usrinput[5:].split(','):
                [var, val] = varval.split('=')
                self.process.variables[var.strip()] = val.strip()
        elif usrinput.startswith('intent'):
            prompt = prompt + "New intent from edge operator: " + usrinput[7:]
        elif usrinput.startswith('cloud'):
            prompt = prompt + "cloud suggests the edge cluster to host {} instances".format(usrinput[len('cloud'):].strip())
        else:
            None
        
        vdict = {k: self.process.variables[k] for k in ('edge_inst', 'edge_cap')}
        self.process.variables['responses'].append({'role': 'user', 'content': json.dumps(vdict)})
        answer = self.gpt_action.run({'type': MessageType.TEXT, 'from': 'edge', 'content': prompt})
        print(answer)
        content:str = answer['content']
        print(content)

        return super().run(message)
    
class ReactToCloudAction(BasicAction):
    def __init__(self, gpt_action, mqtt_responser):
        self.gpt_action = gpt_action
        self.mqtt_responser = mqtt_responser
    
    def traverse(self, fun):
        self.gpt_action.traverse(fun)
        self.mqtt_responser.traverse(fun)
        return super().traverse(fun)
    
    def run(self, message):
        print(message)

        variables = self.process.variables

        if message['from'] == 'operator':
            variables['responses'].append({'role': 'user', 'content': message['content']})
            return super().run(message)

        vdict = {k: variables[k] for k in ('edge_inst', 'edge_cap')}
        variables['responses'].append({'role': 'user', 'content': json.dumps(vdict)})
        message = self.gpt_action.run(message)

        content = json.loads(message['content'])
        print(colored(content.get('command'), 'green'))
        
        edge_inst = content.get('edge_inst')
        if edge_inst:
            self.process.variables.update({'edge_inst':edge_inst})
        answer = {k:content[k] for k in ['edge_inst', 'performance', 'excuse', 'alternatives']}
        answer.update({'note': 'This is the response from the edge'})
        message['content'] = json.dumps(answer)
        message['to'] = 'cloud'

        message = self.mqtt_responser.run(message)
        print("message sent to cloud:")
        print(message['content'])
        return super().run(message)
    

if __name__ == '__main__':
    gpt_act = GptActionWithResponse()
    gpt_act.add_context('system', background)
    mqtt_responser = MQTTResponserAction()
    ui_act = EdgeUiAction(gpt_act, mqtt_responser)
    react_to_cloud = ReactToCloudAction(gpt_act, mqtt_responser)

    process = MQTTProcess(
        name='edge', 
        mqttbroker={'host': 'localhost', 'port': 1883, 'topic': 'cognigpt/dinner-party'},
        actions={
            '_init': WHILE_TRUE(ui_act),
            'react_to_cloud': react_to_cloud
        },
        attentions=[MessageToAttention(['edge', 'all'])]
    )

    process.start(
        message={}, 
        variables={'edge_cap': '20', 'edge_inst': '10', 'responses': []}
    )

    # while True:
    #     ui_act.run({"type": MessageType.TEXT, "from": "cloud", "content": ""})
    # print(process.variables)

