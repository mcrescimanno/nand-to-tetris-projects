#! /usr/bin/python
import sys
import re
import os
import Tree
from JackToken import JackToken
from Constants import *

def _isEmptyString(s):
    return s == empty;

def _isSpace(s):
    return s == space;

def _isNullOrWhitespace(s):
    return s == None or _isEmptyString(s.strip())

def _normalizeLine(line):
    """ Remove any single-line comment on the line and remove leading & trailing whitespace. """
    normalized = line
    commentInx = normalized.find('//')
    
    if commentInx != -1:
        normalized = normalized[0:commentInx]

    normalized = normalized.strip()
    return normalized

def _encodeXmlToken(token):
    if token == "<":
        return "&lt;"
    elif token == ">":
        return "&gt;"
    elif token == "\"":
        return "&quot;"
    elif token == "&":
        return "&amp;"
    else:
        return token
        

class JackTokenizer(object):
    """docstring for JackTokenizer"""
    def __init__(self, inputFilePath, debugMode=False):
        super(JackTokenizer, self).__init__()
        self.inputFilePath = inputFilePath
        self.debugMode = debugMode

        if debugMode:
            normalized = os.path.normpath(inputFilePath)
            outputFilePath = normalized[:-5] + "TDEBUG.xml"
            self.ouputFileObject = open(outputFilePath, 'w')
            self.ouputFileObject.write("<tokens>\n")

        self.fileLines = []

        with open(self.inputFilePath, 'r') as file:
            fileAsString = file.read()
            mCommentsRemoved = self._removeMultilineComments(fileAsString);
            self.fileLines = mCommentsRemoved.split("\n") # may cause issue on Windows with \r or \r\n new lines

        self.currentLineInx = 0
        self.currentLine = self.fileLines[self.currentLineInx]
        self.normalizedLine = _normalizeLine(self.currentLine)

        self.cursorPos = 0;
        self.currentToken = None;

    """ Manage Current Line being Processed """

    def getNextToken(self):
        if self._currentLineHasMoreTokens():
            nextToken = self._getNextToken()
            self._setToken(nextToken)
            return self.currentToken
        elif self._hasMoreLines():
            self._advanceLine()
            return self.getNextToken()
        else:
            if self.debugMode:
                self.ouputFileObject.write("</tokens>")
                self.ouputFileObject.close()

            return None

    def peekNextToken(self):
        return self.peekNextNTokens(1)[0]

    def peekNextNTokens(self, n):
        snap = self._takeSnapshot()
        tokens = []
        for i in range(n):
            tok = self.getNextToken()
            tokens.append(tok)

        self._applyStateChange(snap)
        return tokens

    def _takeSnapshot(self):
        return { "currentLineInx": self.currentLineInx,
                 "currentLine": self.currentLine,
                 "normalizedLine": self.normalizedLine,
                 "cursorPos" : self.cursorPos,
                 "currentToken": self.currentToken
                 }

    def _applyStateChange(self, state):
        self.currentLineInx = state['currentLineInx']
        self.currentLine = state['currentLine']
        self.normalizedLine = state['normalizedLine']
        self.cursorPos = state['cursorPos']
        self.currentToken = state['currentToken']

    def _setToken(self, tokenString):
        self.currentToken = JackToken(tokenString)

        if self.debugMode:
            xml = "<" + self.currentToken.type + "> " + _encodeXmlToken(self.currentToken.token) + " </" + self.currentToken.type + ">\n"
            self.ouputFileObject.write(xml)

    def _advanceLine(self):
        self.currentLineInx = self.currentLineInx + 1
        self.currentLine = self.fileLines[self.currentLineInx]
        self.normalizedLine = self._normalizeLine();

        self.cursorPos = 0

    def _hasMoreLines(self):
        lineCount = len(self.fileLines)
        return lineCount > 0 and self.currentLineInx + 1 < lineCount;

    """ TOKENS """

    def _getNextToken(self):
        token = ""
        lineRemaining = self.normalizedLine[self.cursorPos:]
        isHandlingStringConstant = False;

        for inx,char in enumerate(lineRemaining):
            tokenLength = len(token)

            if isHandlingStringConstant:
                if char != stringDelimeter:
                    token += char
                else:
                    isHandlingStringConstant = False;
                    token += char;
                    self.cursorPos += inx + 1 # move cursor to after this " symbol
                    break;
            else:
                if char == stringDelimeter and tokenLength == 0:
                    isHandlingStringConstant = True;
                    token += char
                elif char == stringDelimeter and tokenLength > 0:
                    # token is already built
                    self.cursorPos += inx # start cursor here for next run.
                    break;
                elif _isSpace(char) and tokenLength == 0:
                    continue;
                elif _isSpace(char) and tokenLength > 0:
                    #token is already built
                    self.cursorPos += inx # start with space on the next run 
                    break;
                elif char in symbols and tokenLength == 0:
                    if inx == 0:
                        token = char;
                        self.cursorPos += 1 # move cursor forward once
                    else:
                        # case where line remaining " {"
                        token = char;
                        self.cursorPos += inx + 1 # move cursor to after the symbol
                    break;
                elif char in symbols and tokenLength > 0:
                    #token is already built
                    self.cursorPos += inx # start with this symbol for next run
                    break;
                else:
                    token += char

        if token == empty:
            raise ValueError("Bad token. Failing line: " + lineRemaining)

        return token

    def _currentLineHasMoreTokens(self):
        return self.cursorPos < len(self.normalizedLine)

    """ Normalize Lines """

    def _removeMultilineComments(self, fullFileText):
        # ref: https://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment       
        return re.sub("\/\*[^*]*\*+(?:[^/*][^*]*\*+)*\/", "", fullFileText);

    def _normalizeLine(self):
        """ Remove any single-line comment on the line and remove leading & trailing whitespace. """
        normalized = self.currentLine
        commentInx = normalized.find('//')
        
        if commentInx != -1:
            normalized = normalized[0:commentInx]

        normalized = normalized.strip()
        return normalized


class CompilationEngine(object):
    """docstring for CompilationEngine"""
    def __init__(self, inputFilePath, debugMode=False):
        super(CompilationEngine, self).__init__()
        normalized = os.path.normpath(inputFilePath)

        self.inputFilePath = normalized
        self.debugMode = debugMode
        if self.debugMode:
            outputFilePath = normalized[:-5] + "DEBUG.xml"
            self.fileObject = open(outputFilePath, 'w')

        self.tokenizer = JackTokenizer(normalized)
        self.treeRoot = None

    """ Tree Generation """

    def _generateTree(self):
        # get first token, and decide which rule to start with (in 99.9% of cases start with 'class' rule)
        nextToken = self.tokenizer.peekNextToken()
        if nextToken == None:
            raise ValueError("No tokens to parse.")
        elif nextToken.getToken() != "class":
            raise ValueError("Program does not begin with a class declaration.")

        root = Tree.Node("class")
        self.compileClass(root)
        self.treeRoot = root # root of tree after it is all built out


    """ JACK Program Structure """

    def compileClass(self, subTreeNode):
        # handle class keyword
        token = self.tokenizer.getNextToken()
        if token.getToken() != 'class':
            raise ValueError("Program does not begin with a class declaration.")
        subTreeNode.addChild(token)

        # handle className
        token = self.tokenizer.getNextToken()
        self.validateClassName(token)
        subTreeNode.addChild(token)

        # handle '{'
        token = self.tokenizer.getNextToken()
        if token.getToken() != "{":
            raise ValueError("Invalid symbol.")
        subTreeNode.addChild(token)

        nextToken = self.tokenizer.peekNextToken()
        while nextToken.getToken() in ["static", "field"]:
            classVarDecSubTree = Tree.Node("classVarDec", subTreeNode.depth + 1)
            self.compileClassVarDec(classVarDecSubTree)
            subTreeNode.addChildTree(classVarDecSubTree)

            nextToken = self.tokenizer.peekNextToken()

        while nextToken.getToken() in ["constructor", "function", "method"]:
            subroutineDecSubTree = Tree.Node("subroutineDec", subTreeNode.depth + 1)
            self.compileSubroutineDec(subroutineDecSubTree)
            subTreeNode.addChildTree(subroutineDecSubTree)

            nextToken = self.tokenizer.peekNextToken()

        # get next token, verify '}' and write symbol (use indent)
        token = self.tokenizer.getNextToken()
        if token.getToken() != "}":
            raise ValueError("Invalid symbol. " + token.getToken())

        subTreeNode.addChild(token)

        return subTreeNode

    def compileClassVarDec(self, subTreeNode):
        # handle 'static' | 'field'
        token = self.tokenizer.getNextToken()
        if token.getToken() not in ['static', 'field']:
            raise ValueError("Class var declaration does not begin with \'static\' or \'field\'.")
        subTreeNode.addChild(token)

        # handle type
        token = self.tokenizer.getNextToken()
        self.validateType(token) #raises error true
        subTreeNode.addChild(token)

        # handle varname
        token = self.tokenizer.getNextToken()
        self.validateVarName(token)
        subTreeNode.addChild(token)

        # handle 0 or more comma separated varnames
        token = self.tokenizer.getNextToken()
        while token.getToken() == ",":
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken()
            self.validateVarName(token)
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken()

        # handle ';'
        if token.getToken() != ";":
            raise ValueError("Class var declaration does not end with a \';\' .")
        subTreeNode.addChild(token)

        return subTreeNode

    def compileSubroutineDec(self, subTreeNode):
        # handle constuctor, function, method
        token = self.tokenizer.getNextToken()
        if token.getToken() not in ['constructor', 'function', 'method']:
            raise ValueError("Subroutine declaration must begin with \'constructor\', \'function\', \'method\'.")
        subTreeNode.addChild(token)

        # handle 'void' | type
        token = self.tokenizer.getNextToken()
        if token.getToken() == "void":
            subTreeNode.addChild(token)
        elif self.validateType(token): # if not validateType, then we necessarily throw error
            subTreeNode.addChild(token)

        # handle subRoutineName
        token = self.tokenizer.getNextToken()
        self.validateSubroutineName(token)
        subTreeNode.addChild(token)

        # handle '('
        token = self.tokenizer.getNextToken()
        if token.getToken() != '(':
            raise ValueError("Expected \'(\' before parameter list.")
        subTreeNode.addChild(token)

        # handle parameterList
        pListSubTreeNode = Tree.Node("parameterList", subTreeNode.depth + 1)
        self.compileParameterList(pListSubTreeNode) # needs to printed like <parameterList></paremeterList> (even if no children)
        subTreeNode.addChildTree(pListSubTreeNode)

        # handle ')'
        token = self.tokenizer.getNextToken()
        if token.getToken() != ')':
            raise ValueError("Expected \')\' after parameter list, but got " + token.getToken() + " instead.")
        subTreeNode.addChild(token)

        # handle subroutineBody
        nextToken = self.tokenizer.peekNextToken()
        if nextToken.getToken() != '{':
            raise ValueError("Expeced \'{\' at start of subroutine body, but received: " + nextToken.getToken())

        subroutineBodySubTreeNode = Tree.Node("subroutineBody", subTreeNode.depth + 1)
        self.compileSubroutineBody(subroutineBodySubTreeNode)
        subTreeNode.addChildTree(subroutineBodySubTreeNode)

        return subTreeNode;

    def compileParameterList(self, subTreeNode):
        nextToken = self.tokenizer.peekNextToken()
        if not self.isType(nextToken):
            return subTreeNode

        token = self.tokenizer.getNextToken()
        # self.validateType(token)
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        self.validateVarName(token)
        subTreeNode.addChild(token)

        # handle 0 or more comma separated (type varname)
        nextToken = self.tokenizer.peekNextToken()
        while nextToken.getToken() == ",":
            token = self.tokenizer.getNextToken() # handle ','
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken() # type
            self.validateType(token)
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken() # varname
            self.validateVarName(token)
            subTreeNode.addChild(token)

            nextToken = self.tokenizer.peekNextToken()

        return subTreeNode

    def compileSubroutineBody(self, subTreeNode):
        token = self.tokenizer.getNextToken()
        if token.getToken() != "{":
            raise ValueError("Expeced \'{\' at start of subroutine body, but received: " + token.getToken())
        subTreeNode.addChild(token)

        # handle 0 or more varDecs
        nextToken = self.tokenizer.peekNextToken()
        while nextToken.getToken() == 'var':
            varDecSubTreeNode = Tree.Node("varDec", subTreeNode.depth + 1)
            self.compileVarDec(varDecSubTreeNode)
            subTreeNode.addChildTree(varDecSubTreeNode)

            nextToken = self.tokenizer.peekNextToken()

        # handle 0 or more statements
        statementsSubTreeNode = Tree.Node("statements", subTreeNode.depth + 1)
        self.compileStatements(statementsSubTreeNode)
        subTreeNode.addChildTree(statementsSubTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != '}':
            raise ValueError("Expeced \'}\' at end of subroutine body, but got " + token.getToken() + " instead.")
        subTreeNode.addChild(token)

        return subTreeNode

    def compileVarDec(self, subTreeNode):
        # handle 'var'
        token = self.tokenizer.getNextToken()
        if token.getToken() != 'var':
            raise ValueError("Variable declaration must begin with \'var\'.")
        subTreeNode.addChild(token)

        # handle type
        token = self.tokenizer.getNextToken()
        self.validateType(token)
        subTreeNode.addChild(token)

        # handle var name
        token = self.tokenizer.getNextToken()
        self.validateVarName(token)
        subTreeNode.addChild(token)

        # handle 0 or more comma separated varnames
        token = self.tokenizer.getNextToken()
        while token.getToken() == ",":
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken()
            self.validateVarName(token)
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken()

        # handle ';'
        if token.getToken() != ';':
            raise ValueError("Variable declaration must end with \';\'.")
        subTreeNode.addChild(token)

        return subTreeNode;

    def isType(self, token):
        tokenType = token.getTokenType()
        tokenVal = token.getToken()

        return tokenVal in primitive_types or self._isIdentifier(token)

    def isClassName(self, token):
        return self._isIdentifier(token)

    def isSubroutineName(self, token):
        return self._isIdentifier(token)

    def isVarName(self, token):
        return self._isIdentifier(token)

    def validateType(self, token):
        tokenType = token.getTokenType()
        tokenVal = token.getToken()
        
        if tokenVal not in primitive_types:
            return self.validateClassName(token)

        return True;

    def validateClassName(self, token):
        if not self._isIdentifier(token):
            raise ValueError("class name \'" + tokenVal + "\' is not a valid identifier.")

        return True;    

    def validateSubroutineName(self, token):
        if not self._isIdentifier(token):
            raise ValueError("subroutine name \'" + tokenVal + "\' is not a valid identifier.")

        return True;

    def validateVarName(self, token):
        if not self._isIdentifier(token):
            raise ValueError("var name \'" + tokenVal + "\' is not a valid identifier.")

        return True;            

    def _isIdentifier(self, token):
        tokenType = token.getTokenType()
        tokenVal = token.getToken()

        return tokenType == t_identifier


    """ JACK Statements """

    def compileStatements(self, subTreeNode):
        nextToken = self.tokenizer.peekNextToken()
        while nextToken.getToken() in ['let', 'if', 'while', 'do', 'return']:
            statementTreeNode = Tree.Node("CHANGEME", subTreeNode.depth + 1)
            if nextToken.getToken() == "let":
                statementTreeNode.setElementName("letStatement")
                self.compileLetStatement(statementTreeNode)
            elif nextToken.getToken() == "if":
                statementTreeNode.setElementName("ifStatement")
                self.compileIfStatement(statementTreeNode)
            elif nextToken.getToken() == "while":
                statementTreeNode.setElementName("whileStatement")
                self.compileWhileStatement(statementTreeNode)
            elif nextToken.getToken() == "do":
                statementTreeNode.setElementName("doStatement")
                self.compileDoStatement(statementTreeNode)
            elif nextToken.getToken() == "return":
                statementTreeNode.setElementName("returnStatement")
                self.compileReturnStatement(statementTreeNode)

            subTreeNode.addChildTree(statementTreeNode)
            nextToken = self.tokenizer.peekNextToken()

        return subTreeNode

    def compileLetStatement(self, subTreeNode):
        token = self.tokenizer.getNextToken()
        if token.getToken() != "let":
            raise ValueError("let statement must begin with let.")
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        self.validateVarName(token)
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        if token.getToken() == "[":
            subTreeNode.addChild(token)

            # handle expression
            exprTreeNode1 = Tree.Node("expression", subTreeNode.depth + 1)
            self.compileExpression(exprTreeNode1)
            subTreeNode.addChildTree(exprTreeNode1)

            token = self.tokenizer.getNextToken()
            if token.getToken() != "]":
                raise ValueError("Expected ].")
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken()

        if token.getToken() != "=":
            raise ValueError("Expected =.")
        subTreeNode.addChild(token)

        # handle expression
        exprTreeNode2 = Tree.Node("expression", subTreeNode.depth + 1)
        self.compileExpression(exprTreeNode2)
        subTreeNode.addChildTree(exprTreeNode2)

        token = self.tokenizer.getNextToken()
        if token.getToken() != ";":
            raise ValueError("Expected ;")
        subTreeNode.addChild(token)

        return subTreeNode;

    def compileIfStatement(self, subTreeNode):
        token = self.tokenizer.getNextToken()
        if token.getToken() != "if":
            raise ValueError("Expected if.")
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        if token.getToken() != "(":
            raise ValueError("Expected \'(\'.")
        subTreeNode.addChild(token)

        ifExprSubTreeNode = Tree.Node("expression", subTreeNode.depth + 1)
        self.compileExpression(ifExprSubTreeNode)
        subTreeNode.addChildTree(ifExprSubTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != ")":
            raise ValueError("Expected \')\'.")
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        if token.getToken() != "{":
            raise ValueError("Expected \'{\'.")
        subTreeNode.addChild(token)

        ifStatementsSubTreeNode = Tree.Node("statements", subTreeNode.depth + 1)
        self.compileStatements(ifStatementsSubTreeNode)
        subTreeNode.addChildTree(ifStatementsSubTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != "}":
            raise ValueError("Expected \'}\'.")
        subTreeNode.addChild(token)

        nextToken = self.tokenizer.peekNextToken()
        if nextToken.getToken() == "else":
            token = self.tokenizer.getNextToken()
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken()
            if token.getToken() != "{":
                raise ValueError("Expected \'{\'.")
            subTreeNode.addChild(token)

            elseStatementsSubTreeNode = Tree.Node("statements", subTreeNode.depth + 1)
            self.compileStatements(elseStatementsSubTreeNode)
            subTreeNode.addChildTree(elseStatementsSubTreeNode)

            token = self.tokenizer.getNextToken()
            if token.getToken() != "}":
                raise ValueError("Expected \'}\'.")
            subTreeNode.addChild(token)

        return subTreeNode

    def compileWhileStatement(self, subTreeNode):
        token = self.tokenizer.getNextToken()
        if token.getToken() != "while":
            raise ValueError("Expected \'while\'.")
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        if token.getToken() != "(":
            raise ValueError("Expected \'(\'.")
        subTreeNode.addChild(token)

        exprSubTreeNode = Tree.Node("expression", subTreeNode.depth + 1)
        self.compileExpression(exprSubTreeNode)
        subTreeNode.addChildTree(exprSubTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != ")":
            raise ValueError("Expected \')\'.")
        subTreeNode.addChild(token)

        token = self.tokenizer.getNextToken()
        if token.getToken() != "{":
            raise ValueError("Expected \'{\'.")
        subTreeNode.addChild(token)        

        whileStatementsSubTreeNode = Tree.Node("statements", subTreeNode.depth + 1)
        self.compileStatements(whileStatementsSubTreeNode)
        subTreeNode.addChildTree(whileStatementsSubTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != "}":
            raise ValueError("Expected \'}\'.")
        subTreeNode.addChild(token)

        return subTreeNode

    def compileDoStatement(self, subTreeNode):
        token = self.tokenizer.getNextToken()
        if token.getToken() != "do":
            raise ValueError("Expected \'do\'.")
        subTreeNode.addChild(token)

        self.compileSubroutineCall(subTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != ";":
            raise ValueError("Expected \';\'.")
        subTreeNode.addChild(token)

        return subTreeNode;

    def compileReturnStatement(self, subTreeNode):
        token = self.tokenizer.getNextToken()
        if token.getToken() != "return":
            raise ValueError("Expected \'return\'.")
        subTreeNode.addChild(token)

        nextToken = self.tokenizer.peekNextToken()
        if nextToken.getToken() != ";":
            exprSubTreeNode = Tree.Node("expression", subTreeNode.depth + 1)
            self.compileExpression(exprSubTreeNode)
            subTreeNode.addChildTree(exprSubTreeNode)

        token = self.tokenizer.getNextToken()
        if token.getToken() != ";":
            raise ValueError("Expected \';\'.")
        subTreeNode.addChild(token)

        return subTreeNode

    """ JACK Expressions """

    def compileExpression(self, subTreeNode):
        termSubTreeNode = Tree.Node("term", subTreeNode.depth + 1)
        self.compileTerm(termSubTreeNode)
        subTreeNode.addChildTree(termSubTreeNode)

        # handle 0 or more (op term)
        nextToken = self.tokenizer.peekNextToken()
        while nextToken.getToken() in ops:
            token = self.tokenizer.getNextToken()
            subTreeNode.addChild(token)

            termSubTreeNode2 = Tree.Node("term", subTreeNode.depth + 1)
            self.compileTerm(termSubTreeNode2)
            subTreeNode.addChildTree(termSubTreeNode2)

            nextToken = self.tokenizer.peekNextToken()

        return subTreeNode

    def compileTerm(self, subTreeNode):
        [t1, t2] = self.tokenizer.peekNextNTokens(2)

        if self.isVarName(t1): #if is varName, then necesarily isSubroutineName and isClassName
            if  t2.getToken() == "[":
                # handle varName [ expression ]
                token = self.tokenizer.getNextToken() # handle varName
                subTreeNode.addChild(token)

                token = self.tokenizer.getNextToken() # handle [
                subTreeNode.addChild(token)

                exprSubTreeNode = Tree.Node("expression", subTreeNode.depth + 1)
                self.compileExpression(exprSubTreeNode)
                subTreeNode.addChildTree(exprSubTreeNode)

                token = self.tokenizer.getNextToken()
                if token.getToken() != "]":
                    raise ValueError("Expected \']\', but received " + token.getToken())
                subTreeNode.addChild(token)

            elif t2.getToken() in [".", "("]:
                self.compileSubroutineCall(subTreeNode)
            else:
                # handle varName
                token = self.tokenizer.getNextToken()
                subTreeNode.addChild(token)

        elif t1.getTokenType() == t_integerConstant:
            const = self.tokenizer.getNextToken()
            subTreeNode.addChild(const)

        elif t1.getTokenType() == t_stringConstant:
            const = self.tokenizer.getNextToken()
            subTreeNode.addChild(const)

        elif t1.getToken() in keywordConstants:
            const = self.tokenizer.getNextToken()
            subTreeNode.addChild(const)

        elif t1.getToken() == "(":
            token = self.tokenizer.getNextToken()
            subTreeNode.addChild(token)

            exprTreeNode = Tree.Node("expression", subTreeNode.depth + 1)
            self.compileExpression(exprTreeNode)
            subTreeNode.addChildTree(exprTreeNode)

            token = self.tokenizer.getNextToken()
            if token.getToken() != ")":
                raise ValueError("Expected \')\'")
            subTreeNode.addChild(token)

        elif t1.getToken() in unaryOps:
            unaryOpToken = self.tokenizer.getNextToken()
            subTreeNode.addChild(unaryOpToken)

            termSubTreeNode = Tree.Node("term", subTreeNode.depth + 1)
            self.compileTerm(termSubTreeNode)
            subTreeNode.addChildTree(termSubTreeNode)
        else:
            raise ValueError("Invalid Term: " + t1.getToken() + ", " + t2.getToken())

        return subTreeNode

    def compileSubroutineCall(self, subTreeNode):
        [t1, t2] = self.tokenizer.peekNextNTokens(2)
        
        self.validateSubroutineName(t1) # also handles the case where (className | varName) bc they are all identifiers.

        if t2.getToken() == "(":
            token = self.tokenizer.getNextToken() # handle subroutineName
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken() # handle (
            subTreeNode.addChild(token)

            exprListTreeNode = Tree.Node("expressionList", subTreeNode.depth + 1)
            self.compileExpressionList(exprListTreeNode)
            subTreeNode.addChildTree(exprListTreeNode)
            
            token = self.tokenizer.getNextToken() # handle )
            subTreeNode.addChild(token)
        elif t2.getToken() == ".":
            token = self.tokenizer.getNextToken() # handle (className | varName)
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken() # handle .
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken() # handle subroutineName
            self.validateSubroutineName(token)
            subTreeNode.addChild(token)

            token = self.tokenizer.getNextToken() # handle (
            if token.getToken() != "(":
                raise ValueError("Expected \'(\'.")
            subTreeNode.addChild(token)

            exprListTreeNode = Tree.Node("expressionList", subTreeNode.depth + 1)
            self.compileExpressionList(exprListTreeNode)
            subTreeNode.addChildTree(exprListTreeNode)

            token = self.tokenizer.getNextToken() # )
            if token.getToken() != ")":
                raise ValueError("Expected \'(\'.")
            subTreeNode.addChild(token)
        else:
            raise ValueError("Expected \'<subroutineName>.\' or \'<className|varName>(\'.")

        return subTreeNode

    def compileExpressionList(self, subTreeNode):
        nextToken = self.tokenizer.peekNextToken() 

        if nextToken.getToken() == ")":
            return subTreeNode
        else:
            exprSubTreeNode = Tree.Node("expression", subTreeNode.depth + 1)
            self.compileExpression(exprSubTreeNode)
            subTreeNode.addChildTree(exprSubTreeNode)

            nextToken = self.tokenizer.peekNextToken()
            while nextToken.getToken() == ",":
                token = self.tokenizer.getNextToken()
                subTreeNode.addChild(token)

                exprSubTreeNode2 = Tree.Node("expression", subTreeNode.depth + 1)
                self.compileExpression(exprSubTreeNode2)
                subTreeNode.addChildTree(exprSubTreeNode2)

                nextToken = self.tokenizer.peekNextToken()

            return subTreeNode;

    """ Writing XML """
    
    def writeXmlOutput(self, treeNode=None):
        if self.debugMode == False:
            print "Cannot write XML Output unless in debugMode."
        else:
            treeNode = self.treeRoot if treeNode is None else treeNode
            indent = "  " * treeNode.depth
            
            if treeNode.isLeaf():
                xml = indent + "<" + treeNode.elementName + "> " + _encodeXmlToken(treeNode.elementVal) + " </" + treeNode.elementName + ">\n"
                self.fileObject.write(xml)
            else:
                outerXmlBeginning = indent + "<" + treeNode.elementName + ">\n"
                outerXmlEnding = indent + "</" + treeNode.elementName + ">\n"

                self.fileObject.write(outerXmlBeginning)
                for child in treeNode.children:
                    self.writeXmlOutput(child)

                self.fileObject.write(outerXmlEnding)

            



    """ Managing Resources """

    def close(self):
        self.fileObject.close()
        



def main():
    try:
        jack_codebase = sys.argv[1]; # can be either a path to a folder or a directory
    except IndexError as e:
        print "Program could not be compiled: No base path to .jack file specified."
        sys.exit()

    # jt = JackTokenizer(jack_codebase)
    # [t1,t2] = jt.peekNextNTokens(2)
    # print t1.getToken(), t2.getToken()
    # # jt.getNextToken()
    # # while token != None:
    # #     print token.getToken(), token.getTokenType()
    # #     token = jt.getNextToken()
    ce = CompilationEngine(jack_codebase, True)
    ce._generateTree()
    ce.writeXmlOutput()
    ce.close()
    
    

if __name__ == '__main__':
    main()