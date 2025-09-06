class ASResult:
    def __init__(self):
        self.error=None
        self.value=None

    def register(self,res):
        if res.error:
            self.error=res.error
        else:
            self.value=res.value
        return res.value
    
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
            self.advance_count += res.advance_count
            if res.error:
                self.error=res.error
            return res.node
    
    def success(self,node):
        self.node=node
        return self
    
    def failure(self,error):
        self.error=error
        return self