"""Module providing basic open ai connection."""

# from os import open
from yaml import safe_load
import openai
from .answers import extract_code

def load_credential():
    if openai.api_key:
        print('already set')
        return
    with open("openai.credential", 'r') as stream:
        credential_data = safe_load(stream)
    openai_config = credential_data['openai']
    openai.api_type = "azure"
    openai.api_base = openai_config['endpoint']
    openai.api_version = "2023-03-15-preview"
    openai.api_key = openai_config["key"]

def one_shot_call(prompt):
    
    messages = [{"role":"user", "content":prompt}]

    load_credential()
    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages = messages,
        temperature=0,
        max_tokens=80,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return response['choices'][0]['message']['content']

### the context will be changed after the call
def call_with_context(context: list, prompt: str, role='user') -> str:
    context.append({'role': role, 'content': prompt})
    load_credential()
    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages = context,
        temperature=0,
        max_tokens=3000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    message = response['choices'][0]['message']
    context.append(message)
    return message['content']


def generate_code(prompt):

    load_credential()
    messages = [
        {
            "role": "system",
            "content": '''you are a python programming master. 
                The user will provide you a short text describing what he or she wants, 
                and you generate pure python code based on the text (not command line) 
                In the end of the generated code, please list all the required libraries, each 
                in a line, as comments'''
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages = messages,
        temperature=0,
        max_tokens=2000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    # print(response)
    content = response['choices'][0]['message']['content']
    code = extract_code(content)
    # print(code)
    return code['code']




if __name__ == "__main__":
    context = []
    while True:
        role = input('role: ')
        prompt = input('prompt: ')
    #     if len(prompt) == 0:
    #         prompt = "please print the first 20 Fibonacci number";
    #     code = generate_code(prompt)
    #     exec(code)
    #     print('\n====source code====')
    #     print(code)
        reply = call_with_context(context, prompt)
        print(reply)