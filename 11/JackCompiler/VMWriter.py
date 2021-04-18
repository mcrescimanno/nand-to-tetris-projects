from Constants import *

class VMWriter(object):
  """docstring for VMWriter"""
  def __init__(self, outputFilePath):
    super(VMWriter, self).__init__()
    self.outputFilePath = outputFilePath
    self.fileObject = open(self.outputFilePath, 'w')

  def close(self):
    if not self.fileObject.closed:
      self.fileObject.close()

  def writeFunction(self, className, functionName, nLocals):
    vmcode = "function " + className + "." + functionName + " " + str(nLocals) + "\n"
    self.fileObject.write(vmcode)

  def writeReturn(self):
    self.fileObject.write("return\n")

  def writeCall(self, className, functionName, nArgs):
    vmcode = "call " + className + "." + functionName + " " + str(nArgs) + "\n"
    self.fileObject.write(vmcode)

  def writeIfGoto(self, label):
    vmcode = "if-goto " + label + "\n"
    self.fileObject.write(vmcode)

  def writeGoto(self, label):
    vmcode = "goto " + label + "\n"
    self.fileObject.write(vmcode)

  def writeLabel(self, label):
    vmcode = "label " + label + "\n"
    self.fileObject.write(vmcode)

  def writePush(self, segment, inx):
    vmcode = "push " + segment + " " + str(inx) + "\n"
    self.fileObject.write(vmcode)

  def writePop(self, segment, inx):
    vmcode = "pop " + segment + " " + str(inx) + "\n"
    self.fileObject.write(vmcode)

  def writeOp(self, operator):
    if operator == "+":
      self.fileObject.write("add\n")
    elif operator == "-":
      self.fileObject.write("sub\n")
    elif operator == "*":
      self.writeCall("Math", "multiply", 2)
    elif operator == "/":
      self.writeCall("Math", "divide", 2)
    elif operator == "&":
      self.fileObject.write("and\n")
    elif operator == "|":
      self.fileObject.write("or\n")
    elif operator == ">":
      self.fileObject.write("gt\n")
    elif operator == "<":
      self.fileObject.write("lt\n")
    elif operator == "=":
      self.fileObject.write("eq\n")

  def writeUnaryOp(self, operator):
    if operator == "-":
      self.fileObject.write("neg\n")
    elif operator == "~":
      self.fileObject.write("not\n")



