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

    def typeOfValue(self,val):
        if isinstance(val,bool):
            return "bool"
        elif isinstance(val,int):
            return "int"
        elif isinstance(val,float):
            return "float"
        elif isinstance(val,str):
            return "string"
        elif val is None or val is "nil":
            return "nil"
        else:
            return "function"
    def visitStatementsNode(self,node,loopContext=None,functionContext=None,parentSymbolTable=None,classContext=None):
        res=ASResult()
        value=[]
        for stmnt in node.statements:
            vl=res.register(self.visit(stmnt,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=parentSymbolTable,classContext=classContext))
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
        
        if right["type"] in ("nil","function") or left["type"] in ("nil","function"):
            return res.failure(f"Binary operation failed: {left['type']} {node.op.type} {right['type']}")
        try:
            if(node.op.type==TokenTypes["TT_PLUS"]):
                ans= left["value"]+right["value"]
            elif(node.op.type==TokenTypes["TT_MINUS"]):
                ans= left["value"]-right["value"]
            elif(node.op.type==TokenTypes["TT_MUL"]):
                ans= left["value"]*right["value"]
            elif(node.op.type==TokenTypes["TT_DIV"]):
                ans= left["value"]/right["value"]
            self.logger.log_binary_operation(left["value"], node.op.type, right["value"], ans)
            result={"type":self.typeOfValue(ans),"value":ans}
            res.success(result)
        except Exception as e:
            self.logger.error(f"Binary operation failed", left=left["type"], operator=node.op.type, right=right["type"], error=str(e))
            res.failure(f"Binary operation failed: {left['type']} {node.op.type} {right['type']}")
        finally:
            return res

    def visitNumberNode(self,node,**kwargs):
        res=ASResult()
        result={
            "type":self.typeOfValue(node.value),
            "value":node.value
        }
        return res.success(result)
    
    def visitBooleanNode(self,node,**kwargs):
        res=ASResult()
        result={
            "type":self.typeOfValue(node.value),
            "value":node.value
        }
        return res.success(result)
    def visitStringNode(self,node,**kwargs):
        res=ASResult()
        result={
            "type":self.typeOfValue(node.value),
            "value":node.value
        }
        return res.success(result)
    
    def visitShowNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        values = []
        for exp in node.body:
            valDict=res.register(self.visit(exp,parentSymbolTable=parentSymbolTable))
            if res.error:
                return res
            values.append(valDict['value'])
        if len(values):
            print(*values)
        else:
            print()
        self.logger.log_show_statement(values)
        return res.success({"value":"nil","type":"nil"})
        
    def visitVariableNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        exp_ans=res.register(self.visit(node.variable_node,parentSymbolTable=parentSymbolTable))
        if not res.error:
            parentSymbolTable.set(node.variable_token_name,value=exp_ans["value"],type=exp_ans["type"],parentSymbolTable=parentSymbolTable)
            self.logger.log_variable_assignment(node.variable_token_name, exp_ans)
            return res.success(exp_ans)
        return res.failure(res.error)

    def visitVariableAccessNode(self,node,parentSymbolTable=None,**kwargs):
        res=ASResult()
        valueDict = parentSymbolTable.get(node.variable_token_name)
        self.logger.log_variable_access(node.variable_token_name, valueDict["value"])
        return res.success(valueDict)
        # error_msg = f"Variable '{node.variable_token_name}' is not defined"
        # self.logger.error(error_msg)
        # return res.failure(error_msg)

    def noVisit(self,node,**kwargs):
        res=ASResult()
        return res.failure(Exception(f"No visit{type(node).__name__} function exists"))

    def visitConditionalNode(self,node,loopContext=None,functionContext=None,parentSymbolTable=None):
        res= ASResult()
        node.symbolTable.parent=parentSymbolTable
        valueDict= res.register(self.visit(node.condition,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        if valueDict["value"]:
            res.register(self.visit(node.body,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            return res.success({"value":True,"type":"bool"})
        else:
            for block in node.elseIfBlockNodes:
                valueDict = res.register(self.visit(block,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=node.symbolTable))
                if res.error:
                    return res
                if valueDict["value"]:
                    return res.success({"value":True,"type":"bool"})
        return res.success(valueDict)

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
            if(node.value=="and"):
                ans=left["value"] and right["value"]
            elif(node.value=="or"):
                ans=left["value"] or right["value"]
            else:
               return  res.failure(f"Unexpected Operator encountered '{node.value}'")
        except Exception as e:
            return res.failure("Error while performing Logical Operation")
        return res.success({"value":ans,"type":self.typeOfValue(ans)})

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
            if(node.value=="gt"):
                ans=left["value"] > right["value"]
            elif(node.value=="gteq"):
                ans=left["value"] >= right["value"]
            elif(node.value=="lt"):
                ans=left["value"] < right["value"]
            elif(node.value=="lteq"):
                ans=left["value"] <= right["value"]
            elif(node.value=="eq"):
                ans=left["value"] == right["value"]
            elif(node.value=="noteq"):
                ans=left["value"] != right["value"]
            else:
               return  res.failure(f"Unexpected Operator encountered '{node.value}'")
        except Exception as e:
            return res.failure("Error while performing Relational Operation")
        return res.success({"value":ans,"type":"bool"})

    def visitTillNode(self,node,functionContext=None,parentSymbolTable=None,**kwargs):
        res=ASResult()
        node.symbolTable.parent=parentSymbolTable
        while True:
            condition_val=res.register(self.visit(node.condition,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            if not condition_val["value"]:
                break
            res.register(self.visit(node.body,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            if node.isStop:
                break
            if node.isContinue:
                node.isContinue=False
            if functionContext is not None and functionContext.isReturn:
                return res.success({"value":True,"type":"bool"})
        return res.success({"value":True,"type":"bool"})
    
    def visitRepeatNode(self,node,functionContext=None,parentSymbolTable=None,**kwargs):
        res=ASResult()
        node.symbolTable.parent=parentSymbolTable
        condition_val=res.register(self.visit(node.condition,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        if condition_val["type"] in ("int","float"):
            condition_val["value"]=int(condition_val["value"])
        else:
            return res.failure(f"Condition must be of type 'INT'")
        if condition_val["value"]<0:
            return res.failure(f"Condition must be greater than zero")
        for _ in range(condition_val["value"]):
            res.register(self.visit(node.body,loopContext=node,functionContext=functionContext,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            if node.isStop:
                break
            if node.isContinue:
                node.isContinue=False
            if functionContext is not None and functionContext.isReturn:
                return res.success({"value":True,"type":"bool"})
        return res.success({"value":True,"type":"bool"})
    def visitStopNode(self,node,loopContext=None,**kwargs):
        res= ASResult()
        if loopContext is None:
            return res.failure("encountered 'stop' statement outside loop")
        loopContext.isStop=True
        return res.success({"value":"nil","type":"nil"})
    
    def visitContinueNode(self,node,loopContext=None,**kwargs):
        res= ASResult()
        if loopContext is None:
            return res.failure("encountered 'continue' statement outside loop")
        loopContext.isContinue=True
        return res.success({"value":"nil","type":"nil"})

    def visitNoneNode(self,node,**kwargs):
        res= ASResult()
        return res.success({"value":"nil","type":"nil"})

    def visitFunctionCallNode(self,node,parentSymbolTable,loopContext=None,**kwargs):
        res= ASResult()
        func=parentSymbolTable.getFunctionDefinition(node.value) #this parentSymbolTable is for the scope when function is called
        node.symbolTable.parent=func["parentSymbolTable"] #this parentSymbolTable is for the scope where function was declared
        if len(func["value"]["params"]) != len(node.args):
            return res.failure(f"Expected {len(func['value']['params'])} arguments but got {len(node.args)}")
        
        for param,arg in zip(func["value"]["params"],node.args):
            arg=res.register(self.visit(arg,parentSymbolTable=node.symbolTable))
            if res.error:
                return res
            node.symbolTable.addArgument(name=node.value,param=param,arg=arg["value"], arg_type=arg["type"])
            
        res.register(self.visit(func["value"]["body"],loopContext=None,functionContext=node,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        if node.isReturn:
            return res.success({"value":node.returnValue["value"],"type":node.returnValue["type"]})
        return res.success({"value":"nil","type":"nil"})

    def visitFunctionDefinitionNode(self,node,parentSymbolTable=None,**kwargs):
        res= ASResult()
        if parentSymbolTable:
            parentSymbolTable.addFunction(name=node.value,body=node.body,params=node.params)
            return res.success({"value":"nil","type":"nil"})
        return res.failure("Encountered Function Definition Outside Global Scope")
        

    def visitReturnNode(self,node,parentSymbolTable,functionContext=None,**kwargs):
        res= ASResult()
        if functionContext is None:
            return res.failure("encountered 'return' statement outside a function")
        functionContext.isReturn=True
        functionContext.returnValue=res.register(self.visit(node.returnNode,parentSymbolTable=parentSymbolTable))
        if res.error:
            return res
        return res.success({"value":"nil","type":"nil"})

    def visitClassDefinitionNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        if parentSymbolTable.isGlobalScope:
            parentSymbolTable.addClassDefinition(node.value,body=node.classBody)
            return res.success(parentSymbolTable.getClassDefinition(node.value))
        return res.failure("Encountered Class Definition In Local Scope")

    def visitInstanceCreationNode(self,node,parentSymbolTable,**kwargs):
        res=ASResult()
        clsDefn = parentSymbolTable.getClassDefinition(node.value)
        node.symbolTable.parent=clsDefn["parentSymbolTable"]
        res.register(self.visit(clsDefn["value"]["body"],loopContext=None,functionContext=None,classContext=node,parentSymbolTable=node.symbolTable))
        if res.error:
            return res
        return res.success({"value":{"symbolTable":node.symbolTable},"type":node.value,"isInstance":True,"parentSymbolTable":node.symbolTable.parent})
    def visit(self,node,loopContext=None,functionContext=None,parentSymbolTable=None,classContext=None):
        method_name=f"visit{type(node).__name__}"
        method=getattr(self,method_name,self.noVisit)
        return method(node,loopContext=loopContext,functionContext=functionContext,parentSymbolTable=parentSymbolTable,classContext=classContext)
    
    
def run(filename):
    logger = get_logger()
    logger.info(f"Starting Rango interpreter execution", filename=filename)
    
    symbol_table = SymbolTable(isGlobalScope=True)
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