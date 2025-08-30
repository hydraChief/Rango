class ASResult:
    def __init__(self):
        self.error=None
        self.value=None

    def register(self,res):
        if res.error:
            self.error=res.none
        return self.value
    
    def failure(self,error):
        self.error=error
        return self
    
    def success(self, value):
        self.value=value
        return self
    
class ParserResult:
    def __init__(self):
        self.error=None
        self.node=None
        self.advance_count=0

    def register_advance(self):
        self.advance_count+=1

    def register(self, res):
        if res is not None:
            if res.error:
                self.advance_count+=res.advance_count
                self.error=res.error
            return self.node
    
    def success(self,node):
        self.node=node
        return self
    
    def failure(self,error):
        self.error=error
        return self