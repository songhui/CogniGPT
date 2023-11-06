import traceback
from .basic_action import BasicAction
from ..gws.message import MessageType, terminate_message

class CodeIncubator(BasicAction):

    def __init__(self):
        self.code_action = None



    def run(self, message):
        # generate code action
        
        if message['type'] == MessageType.DYNAMIC_CODE:
            try:
                code = message['content']
                if not self.code_action:
                    self.code_action = DynamicCode(code)
                else:
                    self.code_action.code = code
                message = message.copy()
                message['note'] = 'code updated' # no need to follow up for source code
                return message
            except Exception as e:
                self.code_action = None
        elif self.code_action:
            self.code_action.process = self.process
            message = self.code_action.run(message)
            return message
        return message

    def traverse(self, fn):
        if self.code_action:
            self.code_action.traverse(fn)
        return super().traverse(fn)    

class DynamicCode(BasicAction):

    def __init__(self, code = ''):
        self.code = code
        super().__init__()

    def run(self, message):
        firstline = self.code.splitlines()[0]
        func_name = None
        if firstline.startswith("#"):
            func_name = firstline[1:].strip()
        elif firstline.startswith("def"):
            i = firstline.find('(')
            func_name = firstline[3:i].strip()

        exec(self.code)
        func = eval(func_name)

        # print(message)
        result = func(message['content'])

        return {'type': MessageType.RETURN, 'content': result}


if __name__ == "__main__":
    sample_code = "# get_system_info\ndef get_system_info(arg):\n    import os\n    import platform\n    if arg == \"info\":\n        print(platform.machine())\n    elif arg == \"cpu\":\n        print(50)\n    else:\n        print(\"I don't understand\")\n\n# platform\n# psutil"
    sample_message = {'type': MessageType.DYNAMIC_CODE, 'content': sample_code}
    incubator = CodeIncubator()
    incubator.run(sample_message)
    
    incubator.run({'type': MessageType.COMMAND, 'content': "info"})
    incubator.run({'type': MessageType.COMMAND, 'content': "nothing"})
    