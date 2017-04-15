from zen.errors import ZenError


class SyntaxError(ZenError):
    def __init__(self, source, position, message):
        super(SyntaxError, self).__init__(message)
        line, column = source.getLocation(position)
        self.line = line
        self.column = column

    def __str__(self):
        return 'SyntaxError ({}:{}) {}'.format(self.line, self.column, self.message)

    def __repr__(self):
        return str(self)
