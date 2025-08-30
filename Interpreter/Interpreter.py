from ErrorHandler import ASResult
from Parser import run as parserRun
class Interpreter():
    def __init__(self):
        self.symbolTable=SymbolTable()

    def visitStatementsNode(self,node):
        res=ASResult()
        value=[]
        for stmnt in node.statements:
            vl=res.register(self.visit(stmnt))
            if res.error:
                return res
            value.append(vl)
        return res.success(value)

    def visitBinaryNode(self,node):
        res=ASResult()

        left =res.register(self.visit(node.left))
        if res.error:
            return res
        right =res.register(self.visit(node.right))
        if res.error:
            return res

        try:
            if(node.op.type=='TT_PLUS'):
                ans= left+right
            elif(node.op.type=='TT_MINUS'):
                ans= left-right
            elif(node.op.type=='TT_MUL'):
                ans= left*right
            elif(node.op.type=='TT_DIV'):
                ans= left/right
            res.success(ans)
        except Exception as e:
            res.failure(e)
        finally:
            return res

    def visitNumberNode(self,node):
        res=ASResult()
        return res.success(node.value)
    
    def visitStringNode(self,node):
        res=ASResult()
        return res.success(node.value)
    
    def visitShowNode(self,node):
        res=ASResult()
        for exp in node.body:
            val=res.register(self.visit(exp))
            if res.error:
                return res
            print(val)
        print()
        return res.success(node.body)
        
    def visitVariableNode(self,node):
        res=ASResult()
        exp_ans=res.register(self.visit(node.variable_node))
        if not res.error:
            self.symbolTable.set(node.variable_token_name,exp_ans)
            return res.success(exp_ans)
        return res.failure(res.error)

    def visitVariableAccessNode(self,node):
        res=ASResult()
        if self.symbolTable.present(node.variable_token_name):
            return res.success(self.symbolTable.get(node.variable_token_name))
        return res.failure("Variable '{node.variable_token_name}' is not defined")

    def noVisit(self,node):
        res=ASResult()
        return res.failure(Exception(f"No visit{type(node).__name__} function exists"))

    def visit(self,node):
        method_name=f"visit{type(node).__name__}"
        method=getattr(self,method_name,self.noVisit)
        return method(node)
    
class SymbolTable:
    def __init__(self):
        self.symbols={}
        self.parent=None

    def set(self,name,value):
        if name in self.symbols:
            raise Exception(f"Variable '{name}' already exists")
        self.symbols[name]=value


    def get(self,name):
        value = self.symbols.get(name)
        if value==None and self.parent:
            return self.parent.get(name)
        elif value==None:
            raise Exception(f"Variable '{name}' not defined")
        return value

    def remove(self,name):
        del self.symbols[name]

    def present(self,name):
        return name in self.symbols

def run(filename):
    symbol_table = SymbolTable()
    interpreter = Interpreter()
    ast, error = parserRun(filename)
    if ast is None:
        return None, "Parser returned None"
    
    if error is None:
        result: ASResult| None = interpreter.visit(ast)
        if result.error:
            return result.value, result.error
        return result.value, error
    else:
        return None, error
    
if __name__=="main":
    run("simply.txt")