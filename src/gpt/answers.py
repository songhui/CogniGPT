def extract_code(content: str):
    result = {'code': '', 'lib': ''}
    code_begin = content.find("```python")
    if code_begin < 0:
        result['code'] = content
        return result
    else:
        code_end = content.find("```", code_begin + 3)
        result['code'] = content[code_begin + 9 :code_end].strip() # + 9 is '```python'

        lib_begin = content.find("```\npip", code_end + 3)
        if lib_begin > 0:
            lib_end = content.find('```', lib_begin)
            after_install = content.find('install', lib_begin) + 7
            result['lib'] = content[after_install : lib_end].strip()

        return result
