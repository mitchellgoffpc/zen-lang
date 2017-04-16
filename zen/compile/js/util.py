from zen.compile.js.ast import *

def JSObject(type, value, **kwargs):
    return Object(values=[
        (String(value='__type'), String(value=type)),
        (String(value='__value'), value)] +
        [(String(value=key), value) for key, value in kwargs.items()])
