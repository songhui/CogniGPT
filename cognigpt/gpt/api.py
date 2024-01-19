"""Module providing basic open ai connection."""

# from os import open
from yaml import safe_load
import openai
from .answers import extract_code

GPT_ENGINE = 'gpt-4'

def load_credential():
    if openai.api_key:
        # print('already set')
        return
    with open("openai.credential", 'r') as stream:
        credential_data = safe_load(stream)
    openai_config = credential_data['openai']
    openai.api_type = "azure"
    openai.azure_endpoint = openai_config['endpoint']
    openai.api_version = "2023-03-15-preview"
    openai.api_key = openai_config["key"]

def call_api(messages):
    load_credential()
    
    return openai.chat.completions.create(
        model=GPT_ENGINE,
        messages = messages,
        max_tokens = 3000
    )

    # try:
    #     return _completion(messages)
    # except openai.error.RateLimitError as error:
    #     error_message = error._message

    # return 

def one_shot_call(prompt):
    
    messages = [{"role":"user", "content":prompt}]

    response = call_api(messages)
    return response.choices[0].message.content

### the context will be changed after the call
def call_with_context(context: list, prompt: str, role='user') -> str:
    context.append({'role': role, 'content': prompt})
    # print(context)
    response = call_api(context)
    message = response.choices[0].message
    context.append({"role": message.role, "content": message.content})
    return message.content

CODE_ORACLE='''
you are a python programming master. \
The user will provide you a short text describing what he or she wants, \
and you generate pure python code based on the text (not command line) \
In the end of the generated code, please list all the required libraries, each \
in a line, as comments. If you were asked to generate a fundtion, you don't need \
to provide the usage of the function, nor the __main__ segment, but the very first line \
of the generated code should be a comment with only the name of the function you generated want the user to call (no other explanations, etc.).
'''
def generate_code(prompt):

  
    messages = [
        {
            "role": "system",
            "content": CODE_ORACLE
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = call_api(messages)
    # print(response)
    content = response.choices[0].message.content
    code = extract_code(content)
    # print(code)
    return code['code']




if __name__ == "__main__":
    context = []
    while True:
        context = [{'role': 'user', 'content':'I will give you a number, and you tell me how it is the sum of two prime numbers'}]
        role = input('role: ')
        prompt = input('prompt: ')

        # Prompt for pcap analysis:  I have a pcap file at "./temp/sample.pcap", could you please generate a python code to analyze the file and print a list of all nodes with the number of incoming traffics to it

        if len(prompt) == 0:
            prompt = "please print the first 20 Fibonacci number";
        code = generate_code(prompt)
        firstline = code.splitlines()[0]
        func_name = None
        if firstline.startswith("#"):
            func_name = firstline[1:].strip()
        elif firstline.startswith("def"):
            i = firstline.find('(')
            func_name = firstline[3:i].strip()

        print(code)
        print(func_name)
        exec(code)
        func = eval(func_name)

        result = func("./temp/sample.pcap")

        print('\n====source code====')
        print(code)
        # reply = call_with_context(context, prompt, role)
        # print(reply)