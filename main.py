class Ast:
  def __init__(self):
    self.linenumber = 0

class Reference(Ast):
  def __init__(self, name):
    self.name = name
    self.owner = None
  def collectvariables(self, index, variables):
    index[self.name]["references"].append(self.owner)
  def __repr__(self):
    return "{}".format(self.name)

class Main(Ast):
  def __init__(self, program):
    super(Main, self).__init__()
    self.program = program

  def collectvariables(self, index, variables):
    for item in self.program:
      item.collectvariables(index, variables)

class Assign(Ast):
  def __init__(self, name, tag, value):
    super(Assign, self).__init__()
    self.name = name
    self.tag = tag
    self.value = value
  def collectvariables(self, index, variables):
    if self.name in index:
      if "references" not in index[self.name]:
        index[self.name]["references"] = []
      index[self.name]["references"].append(self)
    else:
      print("line {}: created variable {}".format(self.linenumber, self.name))
      variable_data = {
        "references": [self],
        "name": self.name,
        "tag": self.tag,
        "startvalue": self.value
      }
      index[self.name] = variable_data
      variables.append(variable_data)

class BinaryOp(Ast):
  def __init__(self, target, left, operator, right):
    super(BinaryOp, self).__init__()
    self.target = target
    self.left = left
    self.operator = operator
    self.right = right

  def collectvariables(self, index, variables):
    self.add_variable(self.left, index, variables)
    self.add_variable(self.right, index, variables)

  def add_variable(self, variable, index, variables):
    if variable not in index:
      pass
      # print("assuming literal {}".format(variable))
    else:
      index[variable]["references"].append(self)

  def __repr__(self):
    return "{} = {} {} {}".format(self.target, self.left, self.operator, self.right)

class MethodCall(Ast):
  def __init__(self, name, arguments):
    super(MethodCall, self).__init__()
    self.name = name
    self.arguments = arguments
    for argument in self.arguments:
      argument.owner = self

  def __repr__(self):  
    return "{}({})".format(self.name, ",".join(map(str, self.arguments)))
  def collectvariables(self, index, variables):
    for argument in self.arguments:
      argument.collectvariables(index, variables)

program1 = Main([
  Assign("a", "mut", 7),
  Assign("b", "mut", 8),
  BinaryOp("a", "a", "+", 6),
  MethodCall("method2", [Reference("a")]),
  BinaryOp("a", "a", "+", 11)
])
from pprint import pprint

def dofirstmove(index, variables):
  for variable in variables:
    moved = False
    for reference in variable["references"]:
      if type(reference) == MethodCall:
        moved = True
        variable["moved"] = reference
      else:
        if moved:
          print("cannot move past borrow")
          print("\tmoved here on line {}: {}".format(variable["moved"].linenumber, variable["moved"]))
          print("\tused here after move here on line {}: {}".format(reference.linenumber, reference))

def borrowcheck(program):
  variables_index = {}
  variables = []
  program.collectvariables(variables_index, variables)
  dofirstmove(variables_index, variables)
  # pprint(variables_index)

def number(program):
  number = 1
  for thing in program.program:
    thing.linenumber = number
    number = number + 1

number(program1)
borrowcheck(program1)
