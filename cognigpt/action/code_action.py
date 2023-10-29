import traceback
from .basic_action import BasicAction, MessageType, terminate_message

class CodeIncubator(BasicAction):

    def _exec(self, message):
        # generate code action
        
        if message['type'] == MessageType.DYNABIC_CODE:
            code = message['content']
            new_action = DynamicCode(code)
            # print(new_action.code)
            old_code_action = self.follow_ups.get('dynabic_code')
            if old_code_action and old_code_action.follow_ups:
                new_action.follow_ups = old_code_action.follow_ups
            else:
                new_action.follow_ups = self.follow_ups.copy()
                self.follow_ups = {}
            self.follow_ups['dynabic_code'] = new_action
            return terminate_message()  # no need to follow up for source code
        return message
        

class DynamicCode(BasicAction):

    def __init__(self, code = '', follow_ups = {}):
        self.code = code
        super().__init__(follow_ups)

    def _exec(self, message):
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
        func(message['content'])

        return {'type': MessageType.RETURN, 'content': ""}


if __name__ == "__main__":
    sample_code = "# get_system_info\ndef get_system_info(arg):\n    import os\n    import platform\n    if arg == \"info\":\n        print(platform.machine())\n    elif arg == \"cpu\":\n        print(50)\n    else:\n        print(\"I don't understand\")\n\n# platform\n# psutil"
    sample_message = {'type': MessageType.DYNABIC_CODE, 'content': sample_code}
    incubator = CodeIncubator()
    incubator.run(sample_message)
    
    incubator.run({'type': MessageType.COMMAND, 'content': "info"})
    incubator.run({'type': MessageType.COMMAND, 'content': "nothing"})
    