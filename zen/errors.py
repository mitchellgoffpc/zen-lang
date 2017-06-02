# ZenError: The base class for all errors thrown by the Zen compiler

class ZenError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'ZenError: {}'.format(message)
