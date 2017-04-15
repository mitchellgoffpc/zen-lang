"""
This file contains some basic error classes thrown by the compiler.
"""

class ZenError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'ZenError: {}'.format(message)
