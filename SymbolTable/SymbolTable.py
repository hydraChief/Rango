class SymbolTable:
    def __init__(self):
        self.symbols={}
        self.parent=None
        self.functions={}


    def functionPresent(self,name):
        return name in self.functions
    
    def functionPresentInScopeChain(self,name):
        return (name in self.functions) or (self.parent and self.parent.functionPresentInScopeChain(name))

    def addFunction(self,name,body,params={}):
        if self.functionPresentInScopeChain(name):
            raise Exception("Function already exists")
        else:
            self.functions[name]={"type":"function","value":{"params":params,"body":body},"parentSymbolTable":self}

    def getFunctionDefinition(self,name):
        if self.functionPresent(name):
            return self.functions[name]
        elif self.present(name) and self.symbols[name]['type']=='function':
            return self.symbols[name]
        elif self.parent:
            return self.parent.getFunctionDefinition(name)
        else:
            raise Exception(f"Function '{name}' not defined")

    def addArgument(self,name,param,arg,arg_type):
        if self.functionPresentInScopeChain(name) or self.presentInScopeChain(name):
            self.set(param,value=arg,type=arg_type)
        else:
            raise Exception(f"Function '{name}' not defined")
        return {param:arg}

    def set(self,name,value='nil',type='nil',parentSymbolTable=None):
        if self.functionPresentInScopeChain(name):
            raise Exception(f"Cannot assign to function '{name}'")
        self.symbols[name]={"type":type,"value":value}
        if parentSymbolTable and type=='function':
            self.symbols[name]["parentSymbolTable"]=parentSymbolTable
        return self.symbols[name]


    def get(self,name):
        value={"type":"nil","value":"nil"}

        if self.functionPresentInScopeChain(name):
            func=self.getFunctionDefinition(name)
            return func
        
        if self.present(name):
            value=self.symbols[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise Exception(f"Variable '{name}' not defined")
        return value

    def remove(self,name):
        del self.symbols[name]

    def present(self,name):
        return name in self.symbols
    
    def presentInScopeChain(self,name):
        return (name in self.symbols) or (self.parent and self.parent.presentInScopeChain(name))

