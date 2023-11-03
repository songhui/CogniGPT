from cognigpt.action.basic_action import PrintMessageAction

if __name__ == "__main__":
    action = PrintMessageAction()
    action.run({'type': 'command', 'content': 'anything'})