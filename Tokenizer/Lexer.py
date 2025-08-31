from .Utility import Position
from .Token import Token
from . import Digits, Letters, KEYWORDS, TokenTypes
class Lexer:
    def __init__(self, text, filename=None):
        self.text = text
        self.filename = filename
        self.pos = Position(-1, 0, -1, filename, text)
        self.current = None
        self.advance()
    
    def create_token(self):
        tokens = []
        while self.current is not None:
            char = self.current
            if char in ' \t':
                self.advance()
            elif char == '\n':
                self.pos.line+=1
                self.pos.col=0
                tokens.append(Token(TokenTypes['TT_NEWLINE'], start=self.pos.copy()))
                self.advance()
            elif char in Digits:
                tokens.append(self.create_number())
            elif char in Letters or char == '_':
                tokens.append(self.create_identifier())
            elif char == '+':
                tokens.append(Token(TokenTypes['TT_PLUS'], value ='+', start=self.pos.copy()))
                self.advance()
            elif char == '-':
                tokens.append(Token(TokenTypes['TT_MINUS'], value='-',start=self.pos.copy()))
                self.advance()
            elif char == '*':
                tokens.append(Token(TokenTypes['TT_MUL'], value ='*', start=self.pos.copy()))
                self.advance()
            elif char == '/':
                tokens.append(Token(TokenTypes['TT_DIV'], value='/',start=self.pos.copy()))
                self.advance()
            elif char == '(':
                tokens.append(Token(TokenTypes['TT_LP'], value='(',start=self.pos.copy()))
                self.advance()
            elif char == ')':
                tokens.append(Token(TokenTypes['TT_RP'], value=')',start=self.pos.copy()))
                self.advance()
            elif char == ';':
                tokens.append(Token(TokenTypes['TT_TERMINATOR'], value=';',start=self.pos.copy()))
                self.advance()
            elif char == ',':
                tokens.append(Token(TokenTypes['TT_SEPERATOR'], value=',',start=self.pos.copy()))
                self.advance()
            elif char == '{':
                tokens.append(Token(TokenTypes['TT_BLOCKSTART'], value='{',start=self.pos.copy()))
                self.advance()
            elif char == '}':
                tokens.append(Token(TokenTypes['TT_BLOCKEND'], value='}',start=self.pos.copy()))
                self.advance()
            elif char in Letters:
                tokens.append(self.create_identifier())
                self.advance()
            else:
                start_pos = self.pos.copy()
                char = self.current
                self.advance()
                return [], f"Invalid syntax, '{char}'"
        tokens.append(Token(TokenTypes['TT_EOF'], start=self.pos.copy()))
        return tokens, None

    def advance(self):
        self.pos.index+=1
        if(self.pos.index<len(self.text)):
            self.current=self.text[self.pos.index]
        else : self.current=None

    def create_number(self):
        num_str=''
        dot_count=0
        start_pos=self.pos.copy()
        while self.current is not None or self.current in Digits+'.':
            if self.current=='.':
                if dot_count==1:break
                dot_count+=1
            num_str+=self.current
            self.advance()

        if dot_count==0: return Token(TokenTypes['TT_INT'],int(num_str),start_pos, self.pos)
        else:
            return Token(TokenTypes['TT_DOUBLE'],float(num_str),start_pos,self.pos)


    def create_string(self):
        id_str=""
        start_pos=self.pos.copy()
        self.advance()
        while self.current is not None and self.current!='"':
            id_str+=self.current
            self.advance()
        if(self.current=='"'):
            return Token(TokenTypes['TT_STRING'],id_str,start_pos,self.pos.copy())
        

    def create_identifier(self):
        id_str=""
        start_pos=self.pos.copy()
        while self.current is not None and self.current in Digits+"_"+self.is_emoji(self.current):
            id_str+=self.current
            self.advance()
        if id_str in KEYWORDS:
            return Token(TokenTypes[KEYWORDS[id_str]],id_str,start_pos,self.pos.copy())
        return Token(TokenTypes['TT_IDENTIFIER'],id_str,start_pos,self.pos.copy())

def tokenGenerator(filename):
    try:
        with open(filename,'r', encoding='utf-8') as f:
            text=f.read()
    except FileNotFoundError:
        return None, f"Error: File '{filename}' not found"
    except Exception as e:
        return None, f"Error: Error reading file: {e}"

    lexer =Lexer(text,filename)
    tokens,error= lexer.create_token()
    return tokens,error