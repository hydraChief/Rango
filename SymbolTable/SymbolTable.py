class SymbolTable:
    def __init__(self):
        self.symbols={}
        self.parent=None

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

