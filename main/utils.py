import inspect
from random import randint

def get_pin():
    return randint(1000, 9999)

def get_username_from_call_stack():
    stack_arr = inspect.stack()
    for item in stack_arr:
        if 'request' in item.frame.f_locals:
            r = item.frame.f_locals['request']
            if type(r).__name__ == 'WSGIRequest':
                if r.user.is_anonymous:
                    return 'anonymous'
                return item.frame.f_locals['request'].user.username
    return 'unknown'