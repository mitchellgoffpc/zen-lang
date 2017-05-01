from zen.compile.js.ast import *

def JSObject(type, **kwargs):
    return Object(values=(
        [(String(value='__type'), String(value=type))] +
        [(String(value=key), value) for key, value in kwargs.items()]))
