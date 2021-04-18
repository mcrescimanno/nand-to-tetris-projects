#! /usr/bin/python
from JackToken import JackToken

class Node(object):
	"""docstring for Node"""
	def __init__(self, value, depth=0):
		super(Node, self).__init__()
		self.elementName = None;
		self.elementVal = None;

		if type(value) is JackToken:
			self.elementName = value.getTokenType()
			self.elementVal = value.getToken()
		elif type(value) is str:
			self.elementName = value
			self.elementVal = None;
		
		self.value = value # is a Token class | value is a string 

		self.depth = depth
		self.children = [] # Array<Node> (order is important)

	def isLeaf(self):
		return len(self.children) == 0 and self.elementName != None and self.elementVal != None

	def addChild(self, nodeVal):
		node = Node(nodeVal, self.depth + 1)
		self.children.append(node)

	def addChildTree(self, node):
		"""IMPORTANT: Caller must make sure node.depth is correct """
		self.children.append(node)

	def setElementName(self, name):
		self.elementName = name

	def walkAndPrint(self):
		indent = "  " * self.depth
		currentTokenValue = indent + self.elementName + " (" + str(self.elementVal) + ")"
		if self.isLeaf():
			print currentTokenValue
		else:
			print currentTokenValue
			for child in self.children:
				child.walkAndPrint()


		
		