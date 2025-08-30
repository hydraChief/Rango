class Token:
    def __init__(self,type,value=None,start=None,end=None):
        self.type = type
        self.value = value
        self.start = start
        self.end = end if end else start
    def __repr__(self):
        if(not self.value):
            return f'Token({self.type})'
        return f'Token({self.type}, {self.value})'
    
