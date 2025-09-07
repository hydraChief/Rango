from SymbolTable import SymbolTable

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
    def __init__(self,value=False):
        self.value= value

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
        self.symbolTable=SymbolTable()

class TillNode:
    def __init__(self,condition,body):
        self.value="till"
        self.condition=condition
        self.body=body
        self.isContinue=False
        self.isStop=False
        self.symbolTable=SymbolTable()

class RepeatNode:
    def __init__(self,condition,body):
        self.value="repeat"
        self.condition=condition
        self.body=body
        self.isContinue=False
        self.isStop=False
        self.symbolTable=SymbolTable()

class StopNode:
    def __init__(self):
        self.value="stop"

class ContinueNode:
    def __init__(self):
        self.value="continue"

class ReturnNode:
    def __init__(self,value):
        self.value=value
        self.returnValue=None

class FunctionDefinitionNode:
    def __init__(self,value,body,params=[]):
        self.value=value
        self.params=params
        self.body=body
class FunctionCallNode:
    def __init__(self,value,args=[]):
        self.value=value
        self.args=args
        self.returnValue=None
        self.isReturn=False
        self.symbolTable=SymbolTable()