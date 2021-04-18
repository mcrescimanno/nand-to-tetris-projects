symbols = ['{', '}', '(', ')', '[', ']', '.', ',',';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var',
             'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 
             'let', 'do', 'if', 'else', 'while', 'return']

t_identifier = "identifier"
t_integerConstant = "integerConstant"
t_stringConstant = "stringConstant"
t_keyword = "keyword"
t_symbol = "symbol"

k_STATIC = "STATIC";
k_FIELD = "FIELD"
k_ARG = "ARG"
k_VAR = "VAR"
kinds = [k_STATIC, k_FIELD, k_ARG, k_VAR]

keywordConstants = ["true", "false", "null", "this"]
unaryOps = ["-", "~"]
ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

ifTrueLabel = "IF_TRUE"
ifFalseLabel = "IF_FALSE"
ifEndLabel = "IF_END"

whileExpLabel = "WHILE_EXP"
whileEndLabel = "WHILE_END"

empty = "";
space = " ";
stringDelimeter = "\""
identifierRegex = r'^[a-zA-Z_]+[a-zA-Z_0-9]*$'

kindToSegmentMap = {k_VAR: "local",
					k_ARG: "argument",
					k_FIELD: "this",
					k_STATIC: "static"}



primitive_types = ["int", "char", "boolean"]