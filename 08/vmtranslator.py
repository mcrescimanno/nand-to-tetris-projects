#! /usr/bin/python

import sys
import re
import os

C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2
C_LABEL = 3
C_IF = 4
C_FUNCTION = 5
C_RETURN = 6
C_CALL = 7
C_NONE = 8

ARITHMETIC_OPS = ["add", "sub", "neg", "gt", "lt", "eq", "and", "or", "not"]
BRANCH_OPS = ["if-goto", "goto"]

arith_ops = {
    "add": "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "M=M+D\n" \
            "@SP\n" \
            "M=M+1\n",

    "sub": "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "M=M-D\n" \
            "@SP\n" \
            "M=M+1\n",

    "neg": "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "M=-M\n" \
            "@SP\n" \
            "M=M+1\n",

    "gt": "@SP\n" \
          "M=M-1\n" \
          "A=M\n" \
          "D=M\n" \
          "@SP\n" \
          "M=M-1\n" \
          "A=M\n" \
          "D=M-D\n" \
          "@__CONDTRUE\n" \
          "D;JGT\n" \
          "D=0\n" \
          "@__CONTINUE\n" \
          "0;JMP\n" \
          "\n" \
          "(__CONDTRUE)\n" \
          "\tD=-1\n" \
          "\t@__CONTINUE\n" \
          "\t0;JMP\n" \
          "\n" \
          "(__CONTINUE)\n" \
          "\t@SP\n" \
          "\tA=M\n" \
          "\tM=D\n" \
          "\t@SP\n" \
          "\tM=M+1\n",

    "eq": "@SP\n" \
          "M=M-1\n" \
          "A=M\n" \
          "D=M\n" \
          "@SP\n" \
          "M=M-1\n" \
          "A=M\n" \
          "D=M-D\n" \
          "@__CONDTRUE\n" \
          "D;JEQ\n" \
          "D=0\n" \
          "@__CONTINUE\n" \
          "0;JMP\n" \
          "\n" \
          "(__CONDTRUE)\n" \
          "\tD=-1\n" \
          "\t@__CONTINUE\n" \
          "\t0;JMP\n" \
          "\n" \
          "(__CONTINUE)\n" \
          "\t@SP\n" \
          "\tA=M\n" \
          "\tM=D\n" \
          "\t@SP\n" \
          "\tM=M+1\n",

    "lt": "@SP\n" \
          "M=M-1\n" \
          "A=M\n" \
          "D=M\n" \
          "@SP\n" \
          "M=M-1\n" \
          "A=M\n" \
          "D=M-D\n" \
          "@__CONDTRUE\n" \
          "D;JLT\n" \
          "D=0\n" \
          "@__CONTINUE\n" \
          "0;JMP\n" \
          "\n" \
          "(__CONDTRUE)\n" \
          "\tD=-1\n" \
          "\t@__CONTINUE\n" \
          "\t0;JMP\n" \
          "\n" \
          "(__CONTINUE)\n" \
          "\t@SP\n" \
          "\tA=M\n" \
          "\tM=D\n" \
          "\t@SP\n" \
          "\tM=M+1\n",

    "and": "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "M=D&M\n" \
            "@SP\n" \
            "M=M+1\n",

    "or": "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "M=D|M\n" \
            "@SP\n" \
            "M=M+1\n",

    "not": "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "M=!M\n" \
            "@SP\n" \
            "M=M+1\n"
}

segment_map = {
    "local": "LCL", # 300
    "argument": "ARG", # 400
    "this": "THIS", # 3000
    "that": "THAT", # 3010
    "pointer": "",
    "temp": "", # 5-12 (8)
    "static": ""
}

def getFilePathsToTranslate(arg, dirname, names):
    for filename in names:
        fullpath = os.path.join(dirname, filename)
        if filename.endswith(".vm") and os.path.isfile(fullpath):
            arg.append(fullpath)

class Parser(object):
    """docstring for Parser"""
    def __init__(self, filepath):
        super(Parser, self).__init__()
        self.filepath = filepath
        self.fileObject = open(filepath, 'r')

        self.currentCommand = None
        self.normalizedCommand = ""
        self.tokens = []

        self.currentCmdCtx = {
            "insideFunction": False,
            "functionName": None
        }

        self.updateCmdCtx = {}

    def close(self):
        self.fileObject.close()

    def hasMoreCommands(self):
        """Are there more commands in the input."""
        return self.currentCommand != ""

    def advance(self):
        """ Reads the next command from the input and makes it the current command. Should only be called if hasMoreCommands is true. Initially there is not current command."""
        self.updateCommandContext();
        self.currentCommand = self.fileObject.readline()
        self.normalizedCommand = self._normalizeCommand()

        if len(self.normalizedCommand) > 0:
            self.tokens = self.normalizedCommand.split(' ')

            if self.tokens[0] == "function":
                functionName = self.tokens[1]
                self.updateCmdCtx = { "insideFunction" : True, "functionName": functionName }

            # elif self.tokens[0] == "return":
            #     self.updateCmdCtx = { "insideFunction": False, "functionName": None }
            
        else:
            self.tokens = []

    def updateCommandContext(self, commandCtxOverride = None):
        updateCtx = self.updateCmdCtx if commandCtxOverride == None else commandCtxOverride;

        if len(updateCtx.keys()) > 0:
            self.currentCmdCtx.update(updateCtx)
        
        self.updateCmdCtx = {}


    def commandType(self):
        """Returns a constant that represents the type of the command. 
        C_ARITHEMTIC is returned for all arithmetic/logical commands."""

        if len(self.tokens) == 0:
            return C_NONE
        elif self.tokens[0] == "push":
            return C_PUSH
        elif self.tokens[0] == "pop":
            return C_POP
        elif self.tokens[0] == "label":
            return C_LABEL
        elif self.tokens[0] in BRANCH_OPS:
            return C_IF
        elif self.tokens[0] in ARITHMETIC_OPS:
            return C_ARITHMETIC
        elif self.tokens[0] == "function":
            return C_FUNCTION
        elif self.tokens[0] == "return":
            return C_RETURN
        elif self.tokens[0] == "call":
            return C_CALL
        else:
            return C_NONE

    def getCommand(self):
        return self.tokens[0]

    def getArgument1(self):
        """string: Returns the first argument of the current command. 
        In the case of C_ARITHMETIC it returns the command itself.
         Should not be called if current command is C_RETURN. """
        ctype = self.commandType()

        if ctype == C_ARITHMETIC:
            return self.tokens[0]
        elif ctype == C_RETURN:
            raise Exception("Cannot call getArgument1 on C_RETURN type command.")
        
        return self.tokens[1]        

    def getArgument2(self):
        """int: Returns the second argument of the current command.
         Should be called only if the current command is C_PUSH,POP,FUNCTION,CALL. """
        ctype = self.commandType()

        if ctype not in [C_POP, C_PUSH, C_FUNCTION, C_CALL]:
            raise Exception("Cannot call getArgument2 because commandType is: " + ctype)

        return int(self.tokens[2])       

    def _normalizeCommand(self):
        """string: # normalize self.currentCommand (remove anything after // comment, also remove \r or \n) """
        normalized = self.currentCommand
        commentInx = normalized.find('//')
        
        if commentInx != -1:
            normalized = normalized[0:commentInx]

        normalized = normalized.strip()
        return normalized


class CodeWriter(object):
    """docstring for CodeWriter"""
    def __init__(self, vm_code_filepath):
        super(CodeWriter, self).__init__()

        normalized = os.path.normpath(vm_code_filepath)

        self.translateDir = os.path.isdir(normalized)
        self.filepathsToTranslate = []

        # Used for appending to jump labels in order to avoid collisions on multiple uses of gt/eq/lt
        self.jump_id = 0

        if self.translateDir:
            # Get all files inside normalized that contain .vm
            os.path.walk(normalized, getFilePathsToTranslate, self.filepathsToTranslate)

            (head,tail) = os.path.split(normalized)
            filename = tail + ".asm"
            outputFilePath = os.path.join(normalized,filename)
            self.fileObject = open(outputFilePath, "w")
        else:
            self.filepathsToTranslate.append(normalized)

            outputFilePath = normalized[:-3] + ".asm"
            self.fileObject = open(outputFilePath, 'w')

        # bootstrapped attributes        
        self.parser = None
        self.fileNamePrefix = None
        

    def load_file(self, file_path):
        """Sets the CodeWriter parser & fileNamePrefix """
        self.parser = Parser(file_path)

        # Gets the path without .vm
        (head,tail) = os.path.split(file_path)
        self.fileNamePrefix = tail[:-3]

    def close_file_parser(self):
        self.parser.close()
        
    def close_output_file(self):
        self.fileObject.close()

    def translate_vm_code(self):
        if self.translateDir:
            self._writeHackMachineBootstrapCode()

        for vm_code_filepath in self.filepathsToTranslate:
            self.load_file(vm_code_filepath);

            while self.parser.hasMoreCommands():
                self.parser.advance()

                self.writeCommand()

            self.close_file_parser()

        if not self.translateDir:
            self._writeEnd()
            
        self.close_output_file()

    def writeCommand(self):
        """void: writes command to file, or throws out command if not a real vm line (ie. comment, space, etc.) """
        ctype = self.parser.commandType()

        if ctype == C_ARITHMETIC:
            self._writeArithmetic()
        elif ctype == C_PUSH:
            self._writePush()
        elif ctype == C_POP:
            self._writePop()
        elif ctype == C_LABEL:
            self._writeLabel()
        elif ctype == C_IF:
            self._writeIf()
        elif ctype == C_FUNCTION:
            self._writeFunction()
        elif ctype == C_RETURN:
            self._writeReturn()
        elif ctype == C_CALL:
            self._writeCall()

    """ WRITE COMMAND HELPERS """

    def _writeEnd(self):
        infiniteLoop = "(__END)\n" \
            "@__END\n" \
            "0;JMP\n"

        self.fileObject.write(infiniteLoop)

    def _writeHackMachineBootstrapCode(self):
        comment = "// HACK bootstrap\n"

        functionName = "Sys.init"
        returnAddressLabel = functionName + "$ret." + str(self.jump_id)
        
        nArgs = 0

        assembly = "@256\n" \
            "D=A\n" \
            "@SP\n" \
            "M=D\n" \
            "@" + returnAddressLabel + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@LCL\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@ARG\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@THIS\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@THAT\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n" \
            "@5\n" \
            "D=A\n" \
            "@" + str(nArgs) + "\n" \
            "D=D+A\n" \
            "@SP\n" \
            "D=M-D\n" \
            "@ARG\n" \
            "M=D\n" \
            "@SP\n" \
            "D=M\n" \
            "@LCL\n" \
            "M=D\n" \
            "@" + functionName + "\n" \
            "0;JMP\n" \
            "(" + returnAddressLabel + ")\n"            

        code = comment + assembly
        self.fileObject.write(code)

        self.jump_id += 1

    def _writeArithmetic(self):
        """void: writes the HACK assembly code to the output file for the given arithmetic command."""
        cmd = self.parser.getArgument1()
        comment = "// " + cmd + "\n"
        assembly = arith_ops.get(cmd)
        if assembly == None:
            raise Exception("command not recognized.")

        if cmd in ["gt","lt","eq"]:
            upper = cmd.upper()
            # find replace all instances of __CONDTRUE AND __CONTINUE to __GT_TRUE_i and __GT_CONT_i
            condtrue_replacement = "__" + upper + "_TRUE_" + str(self.jump_id);
            continue_replacement = "__" + upper + "_CONT_" + str(self.jump_id);
            step1 = re.sub("__CONDTRUE", condtrue_replacement, assembly)

            assembly = re.sub("__CONTINUE", continue_replacement, step1)

            self.jump_id += 1

        code = comment + assembly;
        self.fileObject.write(code)
        
    def _writePush(self):
        segment = self.parser.getArgument1()
        inx = self.parser.getArgument2()
        comment = "// " + self.parser.normalizedCommand + "\n"

        assembly = None;
        if segment == "constant":
            assembly = self._pushConstant(inx)
        else:
            if segment in ["local", "argument", "this", "that"]:
                segment_label = segment_map.get(segment)
                # handle segment_label None
                assembly = self._pushSegment(segment_label, inx)                
            elif segment == "temp":
                assembly = self._pushTemp(inx)                
            elif segment == "pointer":
                assembly = self._pushPointer(inx)                
            elif segment == "static":
                assembly = self._pushStatic(inx)                

        if assembly != None:
            code = comment + assembly
            self.fileObject.write(code)

    def _writePop(self):
        """void: writes to the output file the assembly code that corresponds to the given C_POP command. """
        segment = self.parser.getArgument1()
        inx = self.parser.getArgument2()
        comment = "// " + self.parser.normalizedCommand + "\n"

        assembly = None
        if segment in ["local", "argument", "this", "that"]:
            segment_label = segment_map.get(segment)
            # handle segment_label None
            assembly = self._popSegment(segment_label, inx)            
        elif segment == "temp":
            assembly = self._popTemp(inx)
        elif segment == "pointer":
            assembly = self._popPointer(inx)
        elif segment == "static":
            assembly = self._popStatic(inx)            

        if assembly != None:
            code = comment + assembly
            self.fileObject.write(code)

    def _writeLabel(self):
        label = self._getLabel()        
        comment = self._getCommentString()

        assembly = "(" + label + ")\n"
        code = comment + assembly
        self.fileObject.write(code)

    def _writeIf(self):
        cmd = self.parser.getCommand()
        comment = self._getCommentString()
        label = self._getLabel()

        assembly = None
        if cmd == "goto":
            assembly = "@" + label + "\n" \
                "0;JMP\n"            
        elif cmd == "if-goto":
            branch_true_label = "__BRANCH_TRUE_" + str(self.jump_id)
            branch_false_label = "__BRANCH_FALSE_" + str(self.jump_id)

            assembly = "@SP\n" \
                "M=M-1\n" \
                "A=M\n" \
                "D=M\n" \
                "@" + branch_true_label + "\n" \
                "D;JNE\n" \
                "@" + branch_false_label + "\n" \
                "0;JMP\n" \
                "(" + branch_true_label + ")\n" \
                "\t@" + label + "\n" \
                "\t0;JMP\n" \
                "(" + branch_false_label + ")\n" \
                "0\n"

            self.jump_id += 1
        
        if assembly != None:
            code = comment + assembly
            self.fileObject.write(code)

    def _writeFunction(self):
        comment = self._getCommentString()
        functionName = self.parser.getArgument1()
        functionName = self._normalizeFunctionName(functionName)
        nLocalVars = self.parser.getArgument2()
        label = functionName

        functionLoopLabel = "__FUNCTION_LOOP_" + str(self.jump_id)
        functionContLabel = "__FUNCTION_CONT_" + str(self.jump_id)
        functionPushLabel = "__FUNCTION_PUSH_LOCAL_" + str(self.jump_id)

        assembly = "(" + label + ")\n" \
            "@" + str(nLocalVars) + "\n" \
            "D=A\n" \
            "(" + functionLoopLabel + ")\n" \
            "@" + functionPushLabel + "\n" \
            "D;JNE\n" \
            "@" + functionContLabel + "\n" \
            "0;JMP\n" \
            "(" + functionPushLabel + ")\n" \
            "@SP\n" \
            "A=M\n" \
            "M=0\n" \
            "@SP\n" \
            "M=M+1\n" \
            "D=D-1\n" \
            "@" + functionLoopLabel + "\n" \
            "0;JMP\n" \
            "(" + functionContLabel + ")\n" 

        code = comment + assembly
        self.fileObject.write(code)
        self.jump_id += 1

    def _writeReturn(self):
        comment = self._getCommentString()
        assembly = "@LCL\n" \
            "D=M\n" \
            "@R13\n" \
            "M=D\n" \
            "@5\n" \
            "D=D-A\n" \
            "A=D\n" \
            "D=M\n" \
            "@R14\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@ARG\n" \
            "A=M\n" \
            "M=D\n" \
            "@ARG\n" \
            "D=M\n" \
            "@SP\n" \
            "M=D+1\n" \
            "@R13\n" \
            "D=M\n" \
            "@1\n" \
            "D=D-A\n" \
            "A=D\n" \
            "D=M\n" \
            "@THAT\n" \
            "M=D\n" \
            "@R13\n" \
            "D=M\n" \
            "@2\n" \
            "D=D-A\n" \
            "A=D\n" \
            "D=M\n" \
            "@THIS\n" \
            "M=D\n" \
            "@R13\n" \
            "D=M\n" \
            "@3\n" \
            "D=D-A\n" \
            "A=D\n" \
            "D=M\n" \
            "@ARG\n" \
            "M=D\n" \
            "@R13\n" \
            "D=M\n" \
            "@4\n" \
            "D=D-A\n" \
            "A=D\n" \
            "D=M\n" \
            "@LCL\n" \
            "M=D\n" \
            "@R14\n" \
            "A=M\n" \
            "0;JMP\n"

        code = comment + assembly
        self.fileObject.write(code)

    def _writeCall(self):
        comment = self._getCommentString()
        functionName = self.parser.getArgument1()
        functionName = self._normalizeFunctionName(functionName)
        nArgs = self.parser.getArgument2()

        returnAddressLabel = functionName + "$ret." + str(self.jump_id)

        assembly = "@" + returnAddressLabel + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@LCL\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@ARG\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@THIS\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@THAT\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n" \
            "@5\n" \
            "D=A\n" \
            "@" + str(nArgs) + "\n" \
            "D=D+A\n" \
            "@SP\n" \
            "D=M-D\n" \
            "@ARG\n" \
            "M=D\n" \
            "@SP\n" \
            "D=M\n" \
            "@LCL\n" \
            "M=D\n" \
            "@" + functionName + "\n" \
            "0;JMP\n" \
            "(" + returnAddressLabel + ")\n"

        self.jump_id += 1

        code = comment + assembly
        self.fileObject.write(code)

    """ PUSH HELPERS """

    def _pushConstant(self, i):
        return "@" + str(i) + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n"

    def _pushSegment(self, segment_label, i):
        return "@" + str(segment_label) + "\n" \
            "D=M\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@" + str(i) + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "A=M+D\n" \
            "D=M\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n" \

    def _pushTemp(self, i):
        return "@5\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@" + str(i) + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "A=M+D\n" \
            "D=M\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n" \

    def _pushPointer(self, i):
        this_label = "__COND_THIS_" + str(self.jump_id)
        that_label = "__COND_THAT_" + str(self.jump_id)
        continue_label = "__PTR_CONT_" + str(self.jump_id)

        code = "@" + str(i) + "\n" \
            "D=A\n" \
            "@" + this_label + "\n" \
            "D;JEQ\n" \
            "@" + that_label + "\n" \
            "0;JMP\n" \
            "(" + this_label + ")\n" \
            "\t@THIS\n" \
            "\tD=M\n" \
            "\t@" + continue_label + "\n" \
            "\t0;JMP\n" \
            "(" + that_label + ")\n" \
            "\t@THAT\n" \
            "\tD=M\n" \
            "\t@" + continue_label + "\n" \
            "\t0;JMP\n" \
            "(" + continue_label + ")\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n"

        self.jump_id += 1
        return code

    def _pushStatic(self, inx):
        static_var = self.fileNamePrefix + "." + str(inx)

        return "@" + static_var + "\n" \
            "D=M\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M+1\n"

    """ POP HELPERS """

    def _popSegment(self, segment_label, i):
        return "@" + str(segment_label) + "\n" \
            "D=M\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@" + str(i) + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=M+D\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M-1\n" \

    def _popTemp(self, i):
        return "@5\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=D\n" \
            "@" + str(i) + "\n" \
            "D=A\n" \
            "@SP\n" \
            "A=M\n" \
            "M=M+D\n" \
            "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@SP\n" \
            "M=M+1\n" \
            "A=M\n" \
            "A=M\n" \
            "M=D\n" \
            "@SP\n" \
            "M=M-1\n" \

    def _popPointer(self, i):
        this_label = "__COND_THIS_" + str(self.jump_id)
        that_label = "__COND_THAT_" + str(self.jump_id)
        continue_label = "__PTR_CONT_" + str(self.jump_id)

        code = "@" + str(i) + "\n" \
            "D=A\n" \
            "@" + this_label + "\n" \
            "D;JEQ\n" \
            "@" + that_label + "\n" \
            "0;JMP\n" \
            "(" + this_label + ")\n" \
            "\t@SP\n" \
            "\tM=M-1\n" \
            "\tA=M\n" \
            "\tD=M\n" \
            "\t@THIS\n" \
            "\tM=D\n" \
            "\t@" + continue_label + "\n" \
            "\t0;JMP\n" \
            "(" + that_label + ")\n" \
            "\t@SP\n" \
            "\tM=M-1\n" \
            "\tA=M\n" \
            "\tD=M\n" \
            "\t@THAT\n" \
            "\tM=D\n" \
            "\t@" + continue_label + "\n" \
            "\t0;JMP\n" \
            "(" + continue_label + ")\n" \
            "0\n" \

        self.jump_id += 1
        return code

    def _popStatic(self, inx):
        static_var = self.fileNamePrefix + "." + str(inx)

        return "@SP\n" \
            "M=M-1\n" \
            "A=M\n" \
            "D=M\n" \
            "@" + static_var + "\n" \
            "M=D\n" \

    """ OTHER HELPERS """

    def _getCommentString(self):
        return "// " + self.parser.normalizedCommand + "\n"

    def _normalizeFunctionName(self, functionName):
        return functionName
        # functionNamePrefix = self.fileNamePrefix + "."
        # if functionName.startswith(functionNamePrefix):
        #     return functionName
        # else:
        #     return functionNamePrefix + functionName


    def _getLabel(self):
        """string: Returns the label symbol to be used for handling goto, if-goto, and label commands."""
        functionNamePrefix = self.fileNamePrefix + "."
        label = self.parser.getArgument1()
        if self.parser.currentCmdCtx['insideFunction']:
            functionName = self.parser.currentCmdCtx['functionName'] # Function name should be in form: filename.func
            normalizedName = self._normalizeFunctionName(functionName)
            label = normalizedName + "$" + label

        return label

def main():
    try:
        vm_code_filepath = sys.argv[1];
    except IndexError as e:
        print "Program could not be assembled: No path to asm file specified."

    codeWriter = CodeWriter(vm_code_filepath)
    codeWriter.translate_vm_code()


if __name__ == '__main__':
    main()
        


        