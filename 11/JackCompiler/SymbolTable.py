k_STATIC = "STATIC";
k_FIELD = "FIELD"
k_ARG = "ARG"
k_VAR = "VAR"
kinds = [k_STATIC, k_FIELD, k_ARG, k_VAR]

from Constants import *

class SymbolTable(object):
	"""docstring for SymbolTable

	When compiling an error free jack program, a symbol not 
	found in either table is a subroutineName or a className.

	"""
	def __init__(self):
		super(SymbolTable, self).__init__()
		self.classSymbols = {}
		self.subroutineSymbols = {}
		self.staticVarInx = 0
		self.fieldVarInx = 0
		self.argVarInx = 0
		self.localVarInx = 0

		self.whileLabelInx = 0
		self.ifLabelInx = 0

	def define(self, name, type_, kind):
		""" void : defines a new identifier w/ given properties. STATIC and FIELD (class level), VAR ARG (subroutine level). """
		if kind == k_STATIC:
			existing = self.classSymbols.get(name)
			if existing == None:
				self.classSymbols[name] = (name, type_, kind, self.staticVarInx)
				self.staticVarInx += 1
			else:
				raise IndexError("Cannot have two variables with the same name.")
		elif kind == k_FIELD:
			existing = self.classSymbols.get(name)
			if existing == None:
				self.classSymbols[name] = (name, type_, kind, self.fieldVarInx)
				self.fieldVarInx += 1
			else:
				raise IndexError("Cannot have two variables with the same name.")
		elif kind == k_ARG:
			existing = self.subroutineSymbols.get(name)
			if existing == None:
				self.subroutineSymbols[name] = (name, type_, kind, self.argVarInx)
				self.argVarInx += 1
			else:
				raise IndexError("Cannot have two variables with the same name.")
		elif kind == k_VAR:
			existing = self.subroutineSymbols.get(name)
			if existing == None:
				self.subroutineSymbols[name] = (name, type_, kind, self.localVarInx)
				self.localVarInx += 1
			else:
				raise IndexError("Cannot have two variables with the same name.")
		else:
			raise ValueError(kind + " is not a valid variable KIND (eg. static, field, arg, local).")


	def varCount(self, kind):
		""" int: returns the number of variables of that kind in the given scope. """
		symTable = []
		if kind == k_STATIC or kind == k_FIELD:
			symTable = self.classSymbols
		else:
			symTable = self.subroutineSymbols
				
		s = 0
		for symbol in symTable.values():
			if symbol[2] == kind:
				s += 1

		return s;

	def kindOf(self, name):
		""" string : returns the KIND of the variable `name`. None if no variable found with that name. """
		existing = self.subroutineSymbols.get(name)
		if existing is not None:
			return existing[2]
		else:
			existing = self.classSymbols.get(name)
			return existing[2] if existing is not None else None

	def typeOf(self, name):
		""" string:  ..."""
		existing = self.subroutineSymbols.get(name)
		if existing is not None:
			return existing[1]
		else:
			existing = self.classSymbols.get(name)
			return existing[1] if existing is not None else None

	def indexOf(self, name):
		""" int: ... """
		existing = self.subroutineSymbols.get(name)
		if existing is not None:
			return existing[3]
		else:
			existing = self.classSymbols.get(name)
			return existing[3] if existing is not None else None

	def incrementifLabelInx(self):
		self.ifLabelInx += 1

	def incrementwhileLabelInx(self):
		self.whileLabelInx += 1

	def clearSubroutineSymbols(self):
		self.subroutineSymbols = {}
		self.argVarInx = 0
		self.localVarInx = 0
		self.whileLabelInx = 0
		self.ifLabelInx = 0

	def clearClassSymbols(self):
		self.classSymbols = {}
		self.staticVarInx = 0
		self.fieldVarInx = 0




		