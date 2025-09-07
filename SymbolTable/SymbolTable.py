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
            self.functions[name]={"params":params,"body":body}

    def getFunctionDefinition(self,name):
        value=None
        if self.functionPresent(name):
            value=self.functions[name]
        elif self.parent:
            return self.parent.getFunctionDefinition(name)
        else:
            raise Exception(f"Function '{name}' not defined")
        return value

    def addArgument(self,name,param,arg):
        if self.functionPresentInScopeChain(name):
            self.set(param,arg)
        else:
            raise Exception(f"Function '{name}' not defined")
        return {param:arg}

    def set(self,name,value):
        self.symbols[name]=value
        return value


    def get(self,name):
        value=None
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

