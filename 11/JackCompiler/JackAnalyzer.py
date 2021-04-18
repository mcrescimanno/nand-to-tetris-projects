#! /usr/bin/python
import sys
import re
import os
import Tree
from JackToken import JackToken
from Constants import *
from SymbolTable import SymbolTable
from VMWriter import VMWriter

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

def getFilePathsToCompile(arg, dirname, names):
    for filename in names:
        fullpath = os.path.join(dirname, filename)
        if filename.endswith(".jack") and os.path.isfile(fullpath):
            arg.append(fullpath)
        

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
    def __init__(self, inputFilePath):
        super(CompilationEngine, self).__init__()
        normalized = os.path.normpath(inputFilePath)

        self.compileDir = os.path.isdir(normalized)
        self.jackFilesToCompile = []
        self.inputFilePath = normalized

        if self.compileDir:
            os.path.walk(normalized, getFilePathsToCompile, self.jackFilesToCompile)
        else:
            self.jackFilesToCompile.append(normalized)

        self.tokenizer = None
        self.symbolTable = SymbolTable()
        self.treeRoot = None
        self.currentClassName = None
        self.currentSubroutineContext = None;
        self.writer = None

    """ Load File """
    def loadFile(self, filepath):
        self.tokenizer = JackTokenizer(filepath)
        self._generateTree()
        self._initializeClassDetails(self.treeRoot)

        outputFilePath = filepath[:-5] + ".vm"
        self.writer = VMWriter(outputFilePath)

    def setSubroutineContext(self, ctx):
        self.currentSubroutineContext = ctx

    def compile(self):
        for filepath in self.jackFilesToCompile:
            self.loadFile(filepath)

            self._compileSubroutines()

            self.writer.close()

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

    def _initializeClassDetails(self, treeRoot):
        """ void: Sets self.className and defines all the class level variables in the symbol table. """
        self.symbolTable.clearClassSymbols()

        className = treeRoot.children[1].elementVal
        self.currentClassName = className;

        classVarDecs = [c for c in treeRoot.children if c.elementName == "classVarDec"]
        for cvd in classVarDecs:
            var_info = [c.elementVal for c in cvd.children if c.elementName != "symbol"]
            kind = var_info[0].upper()
            type_ = var_info[1]
            
            for varname in var_info[2:]:
                self.symbolTable.define(varname, type_, kind)
        

    def _compileSubroutines(self):
        """ Initialize the subroutine symbol table  """
        subroutines = [c for c in self.treeRoot.children if c.elementName == "subroutineDec"]
        for node in subroutines:
            self._initializeSubroutineVars(node) # set subroutineCtx & init subroutineSymbolTable
            self._handleSubroutine(node)

    def _initializeSubroutineVars(self, node):
        """ void: sets the subroutineContext and initializes the symbolTable for argument vars """

        self.symbolTable.clearSubroutineSymbols()

        subroutineCtx = {
            "subroutineKind": node.children[0].elementVal, # method,function,constructor
            "voidReturn": node.children[1].elementVal == "void",
            "returnType": node.children[1].elementVal,
            "subroutineName": node.children[2].elementVal
        }

        self.setSubroutineContext(subroutineCtx)

        plistNode = node.children[4]
        arguments = [c for c in plistNode.children if c.elementName != "symbol"]
        if len(arguments) % 2 != 0:
            raise ValueError("REMOVE LATER: Odd number of (type,varname) combos.")

        # if dealing with method, add THIS as arg 0
        if subroutineCtx["subroutineKind"] == "method":
            self.symbolTable.define("this", self.currentClassName, "ARG")

        i = 0
        while i < len(arguments):
            type_ = arguments[i].elementVal
            varname = arguments[i+1].elementVal
            self.symbolTable.define(varname, type_, "ARG")
            i += 2    


    def _handleSubroutine(self, node):
        """ void: 
            1. Initialize Local Vars
            2. Write function vm code
            3. Kick off the compilation of subroutine body
        """
        curSubroutineKind = self.currentSubroutineContext["subroutineKind"]

        subBodyNode = None
        statementsNode = None
        for child in node.children:
            if child.elementName == "subroutineBody":
                subBodyNode = child
                break

        # initialize local vars in symbolTable
        varDecs = [c for c in subBodyNode.children if c.elementName == "varDec"]
        for vd in varDecs:
            locals_ = [c for c in vd.children if c.elementName != "symbol"]
            [varNode,typeNode] = locals_[:2] # var, type
            locals_ = locals_[2:] # varnames only

            type_ = typeNode.elementVal
            for varNode in locals_:
                varname = varNode.elementVal
                self.symbolTable.define(varname, type_, "VAR")
            
        nLocals = self.symbolTable.varCount("VAR")
        self.writer.writeFunction(self.currentClassName, self.currentSubroutineContext["subroutineName"], nLocals)

        if curSubroutineKind == "constructor":
            numFieldVars = self.symbolTable.varCount(k_FIELD)
            self.writer.writePush("constant", numFieldVars)
            self.writer.writeCall("Memory", "alloc", 1)
            self.writer.writePop("pointer", 0) # sets the base address of this
        elif curSubroutineKind == "method":
            self.writer.writePush("argument", 0) # first argument in a method is always the base addr of THIS
            self.writer.writePop("pointer", 0) # anchoring this before method body executes.


        # get statements & handle them
        statementsNode = None
        for child in subBodyNode.children:
            if child.elementName == "statements":
                statementsNode = child
                break

        self._handleSubroutineStatements(statementsNode)

    def _handleSubroutineStatements(self, statementsNode):
        for statement in statementsNode.children:
            if statement.elementName == "letStatement":
                self._handleLetStatement(statement)
            elif statement.elementName == "returnStatement":
                self._handleReturnStatement(statement)
            elif statement.elementName == "doStatement":
                self._handleDoStatement(statement)
            elif statement.elementName == "ifStatement":
                self._handleIfStatement(statement)
            elif statement.elementName == "whileStatement":
                self._handleWhileStatement(statement)

    def _handleLetStatement(self, letStatement):
        

        if letStatement.children[2].elementVal == "=":
            # handle varName = ...
            expr = letStatement.children[3]
            self._handleExpression(expr)

            varname = letStatement.children[1].elementVal
            varKind = self.symbolTable.kindOf(varname)
            segment = kindToSegmentMap[varKind]
            index = self.symbolTable.indexOf(varname)
            self.writer.writePop(segment, index)
        elif letStatement.children[2].elementVal == "[":
            # handle arr[expr1] = expr2
            varname = letStatement.children[1].elementVal
            varKind = self.symbolTable.kindOf(varname)
            segment = kindToSegmentMap[varKind]
            index = self.symbolTable.indexOf(varname)

            bracketExpr = letStatement.children[3]
            self._handleExpression(bracketExpr)

            self.writer.writePush(segment, index) # push varname_base_addr            
            
            self.writer.writeOp("+") # produces add

            rightHandExpr = letStatement.children[6]
            self._handleExpression(rightHandExpr)
            self.writer.writePop("temp", 0) # pop rightHandExpr into temp 0
            self.writer.writePop("pointer", 1) # anchor THAT segment to (bracketExpr + varname_base_addr)
            self.writer.writePush("temp", 0) # push rightHandExpr back onto stack
            self.writer.writePop("that", 0) # pop rightHandExpr into that[0]


    def _handleWhileStatement(self, whileStatement):
        expr = whileStatement.children[2]
        statements = whileStatement.children[5]

        expLabel = whileExpLabel + str(self.symbolTable.whileLabelInx)
        endLabel = whileEndLabel + str(self.symbolTable.whileLabelInx)

        self.symbolTable.incrementwhileLabelInx()

        self.writer.writeLabel(expLabel)
        self._handleExpression(expr)

        self.writer.writeUnaryOp("~") # produces not
        self.writer.writeIfGoto(endLabel)
        self._handleSubroutineStatements(statements)
        self.writer.writeGoto(expLabel)
        self.writer.writeLabel(endLabel)

    def _handleIfStatement(self, ifStatement):
        if len(ifStatement.children) > 7:
            # handle if / else
            trueLabel = ifTrueLabel + str(self.symbolTable.ifLabelInx)
            falseLabel = ifFalseLabel + str(self.symbolTable.ifLabelInx)
            endLabel = ifEndLabel + str(self.symbolTable.ifLabelInx)

            self.symbolTable.incrementifLabelInx()

            expr = ifStatement.children[2]
            trueStatements = ifStatement.children[5]
            elseStatements = ifStatement.children[9]
            self._handleExpression(expr) # expr on top of stack

            self.writer.writeIfGoto(trueLabel)
            self.writer.writeGoto(falseLabel)
            self.writer.writeLabel(trueLabel)

            self._handleSubroutineStatements(trueStatements)
            
            self.writer.writeGoto(endLabel)

            self.writer.writeLabel(falseLabel)
            
            self._handleSubroutineStatements(elseStatements)

            self.writer.writeLabel(endLabel)
        else:
            # handle just if
            trueLabel = ifTrueLabel + str(self.symbolTable.ifLabelInx)
            falseLabel = ifFalseLabel + str(self.symbolTable.ifLabelInx)

            self.symbolTable.incrementifLabelInx()

            expr = ifStatement.children[2]
            trueStatements = ifStatement.children[5]
            self._handleExpression(expr) # expr on top of stack

            self.writer.writeIfGoto(trueLabel)
            self.writer.writeGoto(falseLabel)
            self.writer.writeLabel(trueLabel)

            self._handleSubroutineStatements(trueStatements)

            self.writer.writeLabel(falseLabel)

    def _handleDoStatement(self, doStatement):
        symbol = doStatement.children[2].elementVal
        if symbol == "(":
            className = self.currentClassName
            subroutineName = doStatement.children[1].elementVal
            # assume that we are compiling a Class method which requires the first argument 
            # to be THIS base address.
            self.writer.writePush("pointer", 0) # push this base address as first arg
            expList = doStatement.children[3]
            expressions = [c for c in expList.children if c.elementName == "expression"]
            for e in expressions:
                self._handleExpression(e)

            self.writer.writeCall(className, subroutineName, len(expressions) + 1) # pointer 0 is the default arg0
            self.writer.writePop("temp", 0)
        elif symbol == ".":
            name = doStatement.children[1].elementVal
            isVarName = self.symbolTable.kindOf(name) != None;

            subroutineName = doStatement.children[3].elementVal
            expList = doStatement.children[5]
            expressions = [c for c in expList.children if c.elementName == "expression"]
            
            if isVarName:
                # handle method invocation
                # put the obj base address on the stack
                varKind = self.symbolTable.kindOf(name)
                className = self.symbolTable.typeOf(name)
                segment = kindToSegmentMap[varKind]
                index = self.symbolTable.indexOf(name)
                self.writer.writePush(segment, index)
                # handle remaining expressions
                for e in expressions:
                    self._handleExpression(e)

                nArgs = len(expressions) + 1 # including the object on which the method is being invoked
                self.writer.writeCall(className, subroutineName, nArgs)
            else:
                # handle static function invocation                
                for e in expressions:
                    self._handleExpression(e)

                nArgs = len(expressions)
                self.writer.writeCall(name, subroutineName, nArgs)

            self.writer.writePop("temp", 0)

    def _handleReturnStatement(self, returnStatement):
        if returnStatement.children[1].elementName == "expression":
            # returnStatement.walkAndPrint()
            self._handleExpression(returnStatement.children[1])
            self.writer.writeReturn()
        else:
            self.writer.writePush("constant", 0)
            self.writer.writeReturn()

    def _handleExpression(self, exprTree):
        if len(exprTree.children) == 1:
            termTree = exprTree.children[0]
            self._handleTerm(termTree)
        elif len(exprTree.children) == 0:
            exprTree.prin
        else:
            t1 = exprTree.children[0]
            opTermCombos = exprTree.children[1:]
            
            self._handleTerm(t1)
            i = 0
            while i < len(opTermCombos):
                operation = opTermCombos[i].elementVal
                nextTerm = opTermCombos[i+1]
                self._handleTerm(nextTerm)
                self.writer.writeOp(operation)
                i += 2

    def _handleTerm(self, termTree):
        firstToken = termTree.children[0]
        if len(termTree.children) > 1:
            # handle a[expr] | subroutineCall | (expression) | unaryOp term      
            secondToken = termTree.children[1]
            if firstToken.elementName == "identifier":
                if secondToken.elementVal == "[":
                    # handle a[expr]
                    varname = firstToken.elementVal
                    varKind = self.symbolTable.kindOf(varname)
                    segment = kindToSegmentMap[varKind]
                    index = self.symbolTable.indexOf(varname)

                    self._handleExpression(termTree.children[2])

                    self.writer.writePush(segment, index) # push varname_base_addr
                    
                    self.writer.writeOp("+")
                    self.writer.writePop("pointer", 1)
                    self.writer.writePush("that", 0)

                elif secondToken.elementVal in ["(", "."]:
                    if secondToken.elementVal == "(":
                        # assume that we are compiling a Class method which requires the first argument 
                        # to be THIS base address.
                        self.writer.writePush("pointer", 0) # push this base address as first arg
                        expListNode = termTree.children[2]
                        expressions = [c for c in expListNode.children if c.elementName == "expression"]
                        for e in expressions:
                            self._handleExpression(e)

                        self.writer.writeCall(self.currentClassName, firstToken.elementVal, len(expressions) + 1)
                    elif secondToken.elementVal == ".":
                        name = firstToken.elementVal
                        isVarName = self.symbolTable.kindOf(name) != None;

                        functionName = termTree.children[2].elementVal
                        expListNode = termTree.children[4]
                        expressions = [c for c in expListNode.children if c.elementName == "expression"]
                        
                        if isVarName:
                            varKind = self.symbolTable.kindOf(name)
                            className = self.symbolTable.typeOf(name)
                            segment = kindToSegmentMap[varKind]
                            index = self.symbolTable.indexOf(name)
                            self.writer.writePush(segment, index)

                            for e in expressions:
                                self._handleExpression(e)

                            nArgs = len(expressions) + 1
                            self.writer.writeCall(className, functionName, nArgs)
                        else:
                            for e in expressions:
                                self._handleExpression(e)

                            nArgs = len(expressions)
                            self.writer.writeCall(name, functionName, nArgs)

            elif firstToken.elementName == "symbol":
                if firstToken.elementVal in unaryOps:
                  self._handleTerm(secondToken)
                  self.writer.writeUnaryOp(firstToken.elementVal) # unaryOp term
                else:
                  self._handleExpression(secondToken) # (expression)
        else:
            if firstToken.elementName == t_integerConstant:
                self.writer.writePush("constant", firstToken.elementVal)
            elif firstToken.elementName == t_stringConstant:
                sLength = len(firstToken.elementVal)
                self.writer.writePush("constant", sLength)
                self.writer.writeCall("String", "new", 1)
                for char in firstToken.elementVal:
                    code = ord(char)
                    self.writer.writePush("constant", code)
                    self.writer.writeCall("String", "appendChar", 2)
            elif firstToken.elementName == t_keyword:
                if firstToken.elementVal == "null":
                    self.writer.writePush("constant", 0)
                elif firstToken.elementVal == "false":
                    self.writer.writePush("constant", 0)
                elif firstToken.elementVal == "true":
                    self.writer.writePush("constant", 0)
                    self.writer.writeUnaryOp("~") # produces "not"
                elif firstToken.elementVal == "this":
                    self.writer.writePush("pointer", 0)
            elif firstToken.elementName == t_identifier:
                varKind = self.symbolTable.kindOf(firstToken.elementVal)
                segment = kindToSegmentMap[varKind]
                index = self.symbolTable.indexOf(firstToken.elementVal)
                self.writer.writePush(segment, index)


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

    ce = CompilationEngine(jack_codebase)
    ce.compile()
    
    

if __name__ == '__main__':
    main()