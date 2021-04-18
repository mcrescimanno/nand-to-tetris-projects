import re
from Constants import *

""" TokenType Helper Functions """

def _isKeyword(token):
        return token in keywords

def _isSymbol(token):
    return token in symbols

def _isIntegerConstant(token):
    try:
        num = int(token)
        return num >= 0 and num <= 32767
    except ValueError as e:
        return False;

def _isStringConstant(token):
    inxOfStringsDels = [inx for inx,el in enumerate(token) if el == stringDelimeter]
    return len(inxOfStringsDels) == 2 and inxOfStringsDels[0] == 0 and inxOfStringsDels[1] == len(token) - 1;

def _isIdentifier(token):
    return re.match(identifierRegex, token) != None

def getTokenType(token):
    if _isKeyword(token):
        return t_keyword
    elif _isSymbol(token):
        return t_symbol
    elif _isIntegerConstant(token):
        return t_integerConstant
    elif _isStringConstant(token):
        return t_stringConstant
    elif _isIdentifier(token):
        return t_identifier
    else:
        raise ValueError("Something went wrong with token: " + token)


class JackToken(object):
    """docstring for JackToken"""
    def __init__(self, token):
        super(JackToken, self).__init__()
        tokenType = getTokenType(token)
        if tokenType == "stringConstant":
            token = re.sub("\"", " ", token)

        self.token = token
        self.type = tokenType

    def getToken(self):
        return self.token

    def getTokenType(self):
        return self.type