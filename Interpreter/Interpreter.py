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

    def visitStatementsNode(self,node,loopContext=None,functionContext=None):
        res=ASResult()
        value=[]
        for stmnt in node.statements:
            vl=res.register(self.visit(stmnt,loopContext=loopContext,functionContext=functionContext))
            if res.error:
                return res
            if loopContext is not None and loopContext.isStop:
                return res.success(value)
            value.append(vl)
        return res.success(value)

    def visitBinaryNode(self,node,**kwargs):
        res=ASResult()

        left =res.register(self.visit(node.left))
        if res.error:
            return res
        right =res.register(self.visit(node.right))
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
    
    def visitShowNode(self,node,**kwargs):
        res=ASResult()
        values = []
        for exp in node.body:
            val=res.register(self.visit(exp))
            if res.error:
                return res
            values.append(val)
            print(val)
        print()
        self.logger.log_show_statement(values)
        return res.success(node.body)
        
    def visitVariableNode(self,node,**kwargs):
        res=ASResult()
        exp_ans=res.register(self.visit(node.variable_node))
        if not res.error:
            self.symbolTable.set(node.variable_token_name,exp_ans)
            self.logger.log_variable_assignment(node.variable_token_name, exp_ans)
            return res.success(exp_ans)
        return res.failure(res.error)

    def visitVariableAccessNode(self,node,**kwargs):
        res=ASResult()
        if self.symbolTable.present(node.variable_token_name):
            value = self.symbolTable.get(node.variable_token_name)
            self.logger.log_variable_access(node.variable_token_name, value)
            return res.success(value)
        error_msg = f"Variable '{node.variable_token_name}' is not defined"
        self.logger.error(error_msg)
        return res.failure(error_msg)

    def noVisit(self,node,**kwargs):
        res=ASResult()
        return res.failure(Exception(f"No visit{type(node).__name__} function exists"))

    def visitConditionalNode(self,node,loopContext=None,functionContext=None):
        res= ASResult()
        val= res.register(self.visit(node.condition))
        if res.error:
            return res
        if val:
            res.register(self.visit(node.body,loopContext=loopContext,functionContext=functionContext))
            if res.error:
                return res
            return res.success(True)
        else:
            for block in node.elseIfBlockNodes:
                block_condition = res.register(self.visit(block,loopContext=loopContext,functionContext=functionContext))
                if res.error:
                    return res
                if block_condition:
                    return res.success(True)
        return res.success(val)

    def visitLogicalNode(self,node,**kwargs):
        res=ASResult()
        left=res.register(self.visit(node.left))
        if res.error:
            return res
        right=res.register(self.visit(node.right))
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

    def visitComparatorNode(self,node,**kwargs):
        res=ASResult()
        left=res.register(self.visit(node.left))
        if res.error:
            return res
        right=res.register(self.visit(node.right))
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


    def visitTillNode(self,node,functionContext=None,**kwargs):
        res=ASResult()
        while True:
            condition_val=res.register(self.visit(node.condition,loopContext=node,functionContext=functionContext))
            if res.error:
                return res
            if not condition_val or node.isStop:
                break
            res.register(self.visit(node.body,loopContext=node,functionContext=functionContext))
            if res.error:
                return res
            if functionContext is not None and functionContext.isReturn:
                return res.success(True)
        return res.success(True)
    def visitStopNode(self,node,loopContext=None,**kwargs):
        res= ASResult()
        if loopContext is None:
            return res.failure("encountered 'stop' statement outside loop")
        loopContext.isStop=True
        return res.success(None)

    def visitReturnNode(self,node,functionContext=None,**kwargs):
        res= ASResult()
        if functionContext is None:
            return res.failure("encountered 'return' statement outside a function")
        functionContext.isReturn=True
        return res.success(None)

    def visit(self,node,loopContext=None,functionContext=None):
        method_name=f"visit{type(node).__name__}"
        method=getattr(self,method_name,self.noVisit)
        return method(node,loopContext=loopContext,functionContext=functionContext)
    
    
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
        result: ASResult| None = interpreter.visit(ast)
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