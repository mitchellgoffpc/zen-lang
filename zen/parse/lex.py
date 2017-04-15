"""
Transforms the given source code into a list of tokens
"""

from zen.parse.source import Source


# Operator list:
operators = (
    ';', '$', '%', '&', '*', '+', '-', '/', '<', '=', '>',
    '.', ':', ',', "'",  '!', '?', '@', '^', '|', '~')

butterflies = ('_', '+', '-', '*', '/', '?')


# TokenType enum
class TokenType:
    EOF = 'EOF'
    PAREN_L = '('
    PAREN_R = ')'
    BRACKET_L = '['
    BRACKET_R = ']'
    BRACE_L = '{'
    BRACE_R = '}'
    NAME = 'Name'
    INTEGER = 'Integer'
    FLOAT = 'Float'
    STRING = 'String'
    OPERATOR = 'Operator'


# Token class
class Token:
    def __init__(self, type, start, end, value=None):
        self.type = type
        self.start = start
        self.end = end
        self.value = value

    def __repr__(self):
        if self.value is None:
            return "<Token: {}>".format(self.type)
        else:
            return "<Token: {}, {}>".format(self.type, self.value)


# Lexer class
class Lexer(Source):
    def __init__(self, body):
        super(Lexer, self).__init__(body)
        self.prev_position = 0

    def nextToken(self, reset_position=None):
        if reset_position is None:
            reset_position = self.prev_position
        token = readToken(self, reset_position)
        self.prev_position = token.end
        return token



# Lexing functions
def readToken(source, from_position):
    position = positionAfterWhitespace(source, from_position)

    if position >= source.length:
        return Token(TokenType.EOF, position, position)

    char = source.charAt(position)

    if char.isdigit():
        return readNumber(source, position)
    if char == '_' or char.isalnum():
        return readName(source, position)
    if char == '"':
        return readString(source, position)
    if char in operators:
        return readOperator(source, position)

    if char == '(': return Token(TokenType.PAREN_L, position, position + 1)
    if char == ')': return Token(TokenType.PAREN_R, position, position + 1)
    if char == '[': return Token(TokenType.BRACKET_L, position, position + 1)
    if char == ']': return Token(TokenType.BRACKET_R, position, position + 1)
    if char == '{': return Token(TokenType.BRACE_L, position, position + 1)
    if char == '}': return Token(TokenType.BRACE_R, position, position + 1)

    raise SyntaxError(source.body, position, "Unexpected character: {}".format(char))



def positionAfterWhitespace(source, position):
    while (position < source.length and
           source.charCodeAt(position) in (0x0009, 0x0020, 0x000A, 0x000D)):
        position += 1

    return position



def readNumber(source, start):
    position = start
    is_float = False

    if source.charAt(position) == '0' and source.charAt(position + 1) in ('b', 'B', 'x', 'X'):
        position = readDigits(source, position + 2)
    else:
        position = readDigits(source, position)

    if source.charAt(position) == '.':
        is_float = True
        position = readDigits(source, position + 1)

    if source.charAt(position) in ('e', 'E'):
        is_float = True
        position += 1

        if source.charAt(position) in ('+', '-'):
            position += 1

        position = readDigits(source, position)

    if source.charAt(position) in ('f', 'F', 'd', 'D', 'l', 'L'):
        if is_float and source.charAt(position) in ('l', 'L'):
            raise SyntaxError('Invalid number, float literal cannot use the "L" prefix')

        position += 1

    token_type = (TokenType.FLOAT if is_float
                                  else TokenType.INTEGER)

    return Token(token_type, start, position, source.body[start:position])



def readDigits(source, position):
    if not source.charAt(position).isdigit():
        raise SyntaxError(source.body, position, 'Invalid number, expected digit but got: ' + ord(char))

    while source.charAt(position).isdigit():
        position += 1
    return position



def readString(source, start):
    position = start + 1
    chunk_start = position
    value = ''

    while position < source.length:
        code = source.charCodeAt(position)
        char = chr(code)

        if code == 0xA or code == 0xD or char == '"':
            break
        if code < 0x20 and code != 0x9:
            raise SyntaxError(source.body, position, 'Invalid character within String: ' + code)

        position += 1

        # Read escape sequences
        if char == '\\':
            value += source.body[chunk_start:position-1]
            char = source.charAt(position)

            if char in ['"', '\/', '\\']: value += char
            elif char == 'b': value += '\b'
            elif char == 'f': value += '\f'
            elif char == 'n': value += '\n'
            elif char == 'r': value += '\r'
            elif char == 't': value += '\t'
            elif char == 'u':
                code = source.body[position + 1 : position + 5]
                ucode = getUnicode(code)
                if ucode < 0:
                    raise SyntaxError(source.body, position, 'Invalid character escape sequence: \\u' + code)
                else:
                    value += chr(ucode)
                    position += 4

            else: raise SyntaxError(source.body, position, 'Invalid character escape sequence: \\' + char)

            position += 1
            chunk_start = position

    if char != '"':
        raise SyntaxError(source.body, position, 'Unterminated string')

    return Token(TokenType.STRING, start, position + 1, source.body[start+1:position])



def readName(source, start):
    position = start + 1
    while position < source.length:
        char = source.charAt(position)
        if char in butterflies or char.isalnum():
            position += 1
        else: break

    return Token(TokenType.NAME, start, position, source.body[start:position])




def readOperator(source, start):
    position = start
    char = source.charAt(position)

    if char != ';':
        while (position < source.length and
               source.charAt(position) in operators):
            position += 1

        return Token(TokenType.OPERATOR, start, position, source.body[start:position])

    # Handle comments
    else:
        while (position < source.length and
               source.charAt(position) == ';'):
            position += 1

        level = position - start
        position = positionAfterWhitespace(source, position)
        beginning = position

        while (position < source.length and
               source.charAt(position) != '\n'):
            position += 1

        comment = '(comment :level {} "{}")'.format(level, source.body[beginning:position])
        source.update(source.body[:start] + comment + source.body[position:])
        return source.nextToken(reset_position=start)



# Helper functions
def getUnicode(a, b, c, d):
    return char2hex(a) << 12 | char2hex(b) << 8 | char2hex(c) << 4 | char2hex(d)

def char2hex(c):
    if 48 <= c <= 57: return c - 48
    if 65 <= c <= 70: return c - 55
    if 97 <= c <= 102: return c - 87
    return -1
