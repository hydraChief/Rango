from .SymbolTable import SymbolTable

class ClassSymbolTable(SymbolTable):
    def __init__(self):
        super().__init__()
    
    
    def presentInInheritedScopeChain(self,name):
        return  (not self.isGlobalScope) and ((name in self.symbols) or (self.parent and self.parent.presentInInheritedScopeChain(name)))

    def functionPresentInInheritedScopeChain(self,name):
        return (not self.isGlobalScope) and ((name in self.functions) or (self.parent and self.parent.functionPresentInInheritedScopeChain(name)))

    def getFunctionDefinitionFromInstanceOrInheritedOnly(self, name):
        if not self.isGlobalScope:
            if self.functionPresent(name):
                return self.functions[name]
            elif self.present(name) and self.symbols[name]['type']=='function':
                return self.symbols[name]
            elif self.parent:
                return self.parent.getFunctionDefinitionFromInstanceOrInheritedOnly(name)
        raise Exception(f"Function '{name}' not defined")

    def getFromInstanceOrInheritedOnly(self,name):
        value={"type":"nil","value":"nil","parentSymbolTable":None,"isinstance":False}
        
        if self.functionPresentInInheritedScopeChain(name):
            func=self.getFunctionDefinitionFromInstanceOrInheritedOnly(name)
            return func
        
        if (not self.isGlobalScope) and self.present(name):
            return self.symbols[name]
        elif self.parent:
            return self.parent.get(name)
        
        raise Exception(f"Variable '{name}' not defined")
        
    def setInInstance(self,name,value,type,parentSymbolTable,isInstance=True):
        if self.functionPresentInInheritedScopeChain(name):
            raise Exception(f"Cannot assign to function '{name}'")
        if self.presentInInheritedScopeChain(name):
            if self.present(name):
                self.symbols[name]={"type":type,"value":value}
                if parentSymbolTable and type=='function':
                    self.symbols[name]["parentSymbolTable"]=parentSymbolTable
                self.symbols[name]["isInstance"]=False
                if isInstance:
                    self.symbols[name]["isInstance"]=True
                return self.symbols[name]
            else:
                return self.parent.setInInstance(name,value=value,type=type,parentSymbolTable=parentSymbolTable,isInstance=isInstance)
        else:
            self.symbols[name]={"type":type,"value":value}
            if parentSymbolTable and type=='function':
                self.symbols[name]["parentSymbolTable"]=parentSymbolTable
            self.symbols[name]["isInstance"]=False
            if isInstance:
                self.symbols[name]["isInstance"]=True
            return self.symbols[name]