
def get_response_template(code='0', result={}, source='unknown') -> object:
    template = {
        'code': code,
        'result': result,
        'source': source
    }
    return template