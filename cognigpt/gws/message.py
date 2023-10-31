class MessageType:
    DYNABIC_CODE = 'dynabic_code'
    COMMAND = 'command'
    TERMINATE = 'terminate'
    RETURN = 'return'

def terminate_message():
    return {'type': MessageType.TERMINATE, 'content': ''}  