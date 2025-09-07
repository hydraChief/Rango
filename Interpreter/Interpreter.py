import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ErrorHandler import ASResult
from Parser import run as parserRun
from Logger import get_logger
from Tokenizer import TokenTypes
from SymbolTable import SymbolTable
class Interpreter():
    def __init__(self):
        self.symbolTable=SymbolTable()
        self.logger = get_logger()

    def visitStatementsNode(self,node,loopContext=None,functionContext=None,parentSymbolTable=None):
        res=ASResult()
        value=[]
        for stmnt in node.statements:
            vl=res.register(self.visit(stmnt,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=parentSymbolTable))
            if res.error:
                return res
            if loopContext is not None and (loopContext.isStop or loopContext.isContinue):
                return res.success(value)
            if functionContext is not None and functionContext.isReturn:
                return res.success(value)
            value.append(vl)
        return res.success(value)

    def visitBinaryNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()

        left =res.register(self.visit(node.left,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        right =res.register(self.visit(node.right,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        ans=None
        try:
            if(node.op.type==TokenTypes['TT_PLUS']):
                ans= left+right
            elif(node.op.type==TokenTypes['TT_MINUS']):
                ans= left-right
            elif(node.op.type==TokenTypes['TT_MUL']):
                ans= left*right
            elif(node.op.type==TokenTypes['TT_DIV']):
                ans= left/right
            self.logger.log_binary_operation(left, node.op.type, right, ans)
            res.success(ans)
        except Exception as e:
            self.logger.error(f"Binary operation failed", left=str(left), operator=node.op.type, right=str(right), error=str(e))
            res.failure(e)
        finally:
            return res

    def visitNumberNode(self,node,**kwargs):
        res=ASResult()
        return res.success(node.value)
    
    def visitBooleanNode(self,node,**kwargs):
        res=ASResult()
        return res.success(node.value)

    def visitStringNode(self,node,**kwargs):
        res=ASResult()
        return res.success(node.value)
    
    def visitShowNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        values = []
        for exp in node.body:
            val=res.register(self.visit(exp,parentSymbolTable=parentSymbolTable))
            if res.error:
                return res
            values.append(val)
        if len(values):
            print(*values)
        else:
            print()
        self.logger.log_show_statement(values)
        return res.success(node.body)
        
    def visitVariableNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        exp_ans=res.register(self.visit(node.variable_node,parentSymbolTable=parentSymbolTable))
        if not res.error:
            parentSymbolTable.set(node.variable_token_name,exp_ans)
            self.logger.log_variable_assignment(node.variable_token_name, exp_ans)
            return res.success(exp_ans)
        return res.failure(res.error)

    def visitVariableAccessNode(self,node,parentSymbolTable=None,**kwargs):
        res=ASResult()
        if parentSymbolTable.presentInScopeChain(node.variable_token_name):
            value = parentSymbolTable.get(node.variable_token_name)
            self.logger.log_variable_access(node.variable_token_name, value)
            return res.success(value)
        error_msg = f"Variable '{node.variable_token_name}' is not defined"
        self.logger.error(error_msg)
        return res.failure(error_msg)

    def noVisit(self,node,**kwargs):
        res=ASResult()
        return res.failure(Exception(f"No visit{type(node).__name__} function exists"))

    def visitConditionalNode(self,node,loopContext=None,functionContext=None,parentSymbolTable=None):
        res= ASResult()
        node.symbolTable.parent=parentSymbolTable
        val= res.register(self.visit(node.condition,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        if val:
            res.register(self.visit(node.body,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            return res.success(True)
        else:
            for block in node.elseIfBlockNodes:
                block_condition = res.register(self.visit(block,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=node.symbolTable))
                if res.error:
                    return res
                if block_condition:
                    return res.success(True)
        return res.success(val)

    def visitLogicalNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        left=res.register(self.visit(node.left,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        right=res.register(self.visit(node.right,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        ans=None
        try:
            if(node.value=='and'):
                ans=left and right
            elif(node.value=='or'):
                ans=left or right
            else:
               return  res.failure(f"Unexpected Operator encountered '{node.value}'")
        except Exception as e:
            return res.failure("Error while performing Logical Operation")
        return res.success(ans)

    def visitComparatorNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        left=res.register(self.visit(node.left,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        right=res.register(self.visit(node.right,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        ans=False
        try:
            if(node.value=='gt'):
                ans=left > right
            elif(node.value=='gteq'):
                ans=left >= right
            elif(node.value=='lt'):
                ans=left < right
            elif(node.value=='lteq'):
                ans=left <= right
            elif(node.value=='eq'):
                ans=left == right
            elif(node.value=='noteq'):
                ans=left != right
            else:
               return  res.failure(f"Unexpected Operator encountered '{node.value}'")
        except Exception as e:
            return res.failure("Error while performing Relational Operation")
        return res.success(ans)

    def visitTillNode(self,node,functionContext=None,parentSymbolTable=None,**kwargs):
        res=ASResult()
        node.symbolTable.parent=parentSymbolTable
        while True:
            condition_val=res.register(self.visit(node.condition,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            if not condition_val:
                break
            res.register(self.visit(node.body,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            if node.isStop:
                break
            if node.isContinue:
                node.isContinue=False
            if functionContext is not None and functionContext.isReturn:
                return res.success(True)
        return res.success(True)
    
    def visitRepeatNode(self,node,functionContext=None,parentSymbolTable=None,**kwargs):
        res=ASResult()
        node.symbolTable.parent=parentSymbolTable
        condition_val=res.register(self.visit(node.condition,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        if type(condition_val).__name__ in ("int","float"):
            condition_val=int(condition_val)
        else:
            return res.failure(f"Condition must be of type 'INT'")
        if condition_val<0:
            return res.failure(f"Condition must be greater than zero")
        for _ in range(condition_val):
            res.register(self.visit(node.body,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            if node.isStop:
                break
            if node.isContinue:
                node.isContinue=False
            if functionContext is not None and functionContext.isReturn:
                return res.success(True)
        return res.success(True)
    def visitStopNode(self,node,loopContext=None,**kwargs):
        res= ASResult()
        if loopContext is None:
            return res.failure("encountered 'stop' statement outside loop")
        loopContext.isStop=True
        return res.success(None)
    
    def visitContinueNode(self,node,loopContext=None,**kwargs):
        res= ASResult()
        if loopContext is None:
            return res.failure("encountered 'continue' statement outside loop")
        loopContext.isContinue=True
        return res.success(None)

    def visitFunctionCallNode(self,node,parentSymbolTable,loopContext=None,**kwargs):
        res= ASResult()
        node.symbolTable.parent=parentSymbolTable
        func=node.symbolTable.getFunctionDefinition(node.value)
        if len(func["params"]) != len(node.args):
            return res.failure(f"Expected {len(func['params'])} arguments but got {len(node.args)}")
        
        for param,arg in zip(func["params"],node.args):
            arg=res.register(self.visit(arg,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            node.symbolTable.addArgument(name=node.value,param=param,arg=arg)
            
        res.register(self.visit(func["body"],loopContext=None,functionContext=node,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        if node.isReturn:
            return res.success(node.returnValue)
        return res.success(None)

    def visitFunctionDefinitionNode(self,node,parentSymbolTable=None,**kwargs):
        res= ASResult()
        if parentSymbolTable:
            parentSymbolTable.addFunction(name=node.value,body=node.body,params=node.params)
            return res.success(None)
        return res.failure("Encountered Function Definition Outside Global Scope")
        

    def visitReturnNode(self,node,parentSymbolTable,functionContext=None,**kwargs):
        res= ASResult()
        if functionContext is None:
            return res.failure("encountered 'return' statement outside a function")
        functionContext.isReturn=True
        functionContext.returnValue=res.register(self.visit(node.returnValue,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        return res.success(None)

    def visit(self,node,loopContext=None,functionContext=None,parentSymbolTable=None):
        method_name=f"visit{type(node).__name__}"
        method=getattr(self,method_name,self.noVisit)
        return method(node,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=parentSymbolTable)
    
    
def run(filename):
    logger = get_logger()
    logger.info(f"Starting Rango interpreter execution", filename=filename)
    
    symbol_table = SymbolTable()
    interpreter = Interpreter()
    
    logger.info("Calling parser...")
    ast, error = parserRun(filename)
    
    if ast is None:
        logger.error("Parser returned None")
        return None, "Parser returned None"
    
    if error is None:
        logger.log_interpretation_start()
        result: ASResult| None = interpreter.visit(ast,parentSymbolTable=symbol_table)
        if result.error:
            logger.log_interpretation_error(result.error)
            return result.value, result.error
        logger.log_interpretation_complete(result.value)
        logger.log_session_end()
        return result.value, error
    else:
        logger.error(f"Parser error occurred", error=str(error))
        logger.log_session_end()
        return None, error
    
if __name__ == "__main__":
    run("simply.txt")