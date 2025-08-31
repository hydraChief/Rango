class BinaryNode:
    def __init__(self,left=None,op=None,right=None):
        self.type="BN"
        self.left=left
        self.right=right
        self.op=op

class NumberNode:
    def __init__(self,value):
        self.type="N"
        self.value=value

class StringNode:
    def __init__(self,value):
        self.type='S'
        self.value=value

class StatementsNode:
    def __init__(self,statements):
        self.statements=statements

class ShowNode:
    def __init__(self,body):
        self.body=body

class VariableNode:
    def __init__(self,variable_token_name,variable_node):
        self.variable_token_name=variable_token_name
        self.variable_node=variable_node

class VariableAccessNode:
    def __init__(self,variable_token_name):
        self.variable_token_name=variable_token_name

class BooleanNode:
    def __init__(self,value):
        self.value= True if value in ("true") else False

class ComparatorNode:
    def __init__(self,left,value,right):
        self.value=value
        self.left=left
        self.right=right

class LogicalNode:
    def __init__(self,value,left,right):
        self.value=value
        self.left=left
        self.right=right

class ConditionalNode:
    def __init__(self,value,condition,body=[],elseIfBlockNodes=[]):
        self.value=value
        self.condition=condition
        self.body=body
        self.elseIfBlockNodes=elseIfBlockNodes