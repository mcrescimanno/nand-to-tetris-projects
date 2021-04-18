symbols = ['{', '}', '(', ')', '[', ']', '.', ',',';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var',
             'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 
             'let', 'do', 'if', 'else', 'while', 'return']

t_identifier = "identifier"
t_integerConstant = "integerConstant"
t_stringConstant = "stringConstant"
t_keyword = "keyword"
t_symbol = "symbol"

keywordConstants = ["true", "false", "null", "this"]
unaryOps = ["-", "~"]
ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

empty = "";
space = " ";
stringDelimeter = "\""
identifierRegex = r'^[a-zA-Z_]+[a-zA-Z_0-9]*$'



primitive_types = ["int", "char", "boolean"]