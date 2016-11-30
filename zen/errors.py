"""
This file contains some basic error classes thrown by the compiler.
"""

class ZenError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'ZenError: {}'.format(message)


class SyntaxError(ZenError):
    def __init__(self, source, position, message):
        super(SyntaxError, self).__init__(message)
        line, column = self.getLocation(source, position)
        self.line = line
        self.column = column

    def __str__(self):
        return 'SyntaxError ({}:{}) {}'.format(self.line, self.column, self.message)

    def __repr__(self):
        return str(self)

    def getLocation(self, source, position):
        lines = source.body[:position].splitlines()
        if lines:
            line = len(lines)
            column = len(lines[-1]) + 1
        else:
            line = 1
            column = 1
        return line, column
