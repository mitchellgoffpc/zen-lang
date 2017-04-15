"""
Provides a class to hold the source code.
"""

class Source(object):
    def __init__(self, body):
        self.update(body)

    def update(self, body):
        self.body = body
        self.length = len(body)

    def charCodeAt(self, index):
        code = ord(self.body[index])
        if code < 0x0020 and code not in (0x0009, 0x000A, 0x000D):
            raise SyntaxError(self.body, index, "Invalid character: " + code)
        else:
            return code

    def charAt(self, index):
        return chr(self.charCodeAt(index))

    def getLocation(self, position):
        lines = self.body[:position].split('\n')

        if lines:
            line = len(lines)
            column = len(lines[-1]) + 1
            return line, column
        else:
            return (1, 1)
