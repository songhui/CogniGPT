class MessageType:
    DYNAMIC_CODE = 'dynamic_code'
    COMMAND = 'command'
    TERMINATE = 'terminate'
    RETURN = 'return'
    TEXT = 'text'
    

def terminate_message():
    return {'type': MessageType.TERMINATE, 'content': ''}  