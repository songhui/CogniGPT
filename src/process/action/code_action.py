from basic_action import BasicAction, MessageType
import traceback

class CodeIncubator(BasicAction):
    def run(self, message):
        # generate code action
        try:
            if message['type'] == MessageType.DYNABIC_CODE:
                code = message['content']
                new_action = DynamicCode(code)
                print(new_action.code)
                self.follow_ups['dynabic_code'] = new_action
        except: # only if it is not code, go to subsequent actions
            # traceback.print_exc()
            super().run(message)

class DynamicCode(BasicAction):

    def __init__(self, code = '', follow_ups = {}):
        self.code = code
        super().__init__(follow_ups)

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

        func(message)

        return super().run(message)


if __name__ == "__main__":
    sample_code = "# get_system_info\ndef get_system_info(arg):\n    import os\n    import platform\n    if arg == \"info\":\n        print(platform.machine())\n    elif arg == \"cpu\":\n        print(50)\n    else:\n        print(\"I don't understand\")\n\n# platform\n# psutil"
    sample_message = {'type': MessageType.DYNABIC_CODE, 'content': sample_code}
    incubator = CodeIncubator()
    incubator.run(sample_message)
    
    incubator.run("info")
    incubator.run('nothing')
    